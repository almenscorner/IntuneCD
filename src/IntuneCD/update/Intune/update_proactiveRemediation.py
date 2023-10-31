#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Proactive Remediation in Intune.
"""

import base64
import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.check_file import check_file
from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.graph_batch import batch_assignment, get_object_assignment
from ...intunecdlib.graph_request import (
    makeapirequest,
    makeapirequestDelete,
    makeapirequestPatch,
    makeapirequestPost,
)
from ...intunecdlib.load_file import load_file
from ...intunecdlib.remove_keys import remove_keys
from .update_assignment import post_assignment_update, update_assignment

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceHealthScripts"


def update(
    path, token, assignment=False, report=False, create_groups=False, remove=False
):
    """
    This function updates all Proactive Remediation in Intune if,
    the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_summary = []
    # Set Powershell script path
    configpath = f"{path}/Proactive Remediations"
    # If Powershell script path exists, continue
    if os.path.exists(configpath):
        # Get Proactive remediation's
        mem_proactiveRemediation = makeapirequest(ENDPOINT, token)
        # Get current assignment
        mem_assignments = batch_assignment(
            mem_proactiveRemediation,
            "deviceManagement/deviceHealthScripts/",
            "/assignments",
            token,
        )

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            # Check which format the file is saved as then open file, load data
            # and set query parameter
            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)

            # Create object to pass in to assignment function
            assign_obj = {}
            if "assignments" in repo_data:
                assign_obj = repo_data["assignments"]
            repo_data.pop("assignments", None)

            data = {"value": ""}
            if mem_proactiveRemediation["value"]:
                for val in mem_proactiveRemediation["value"]:
                    if repo_data["displayName"] == val["displayName"]:
                        data["value"] = val
                        mem_proactiveRemediation["value"].remove(val)

            # If Powershell script exists, continue
            if data["value"]:
                print("-" * 90)
                q_param = None
                # Get Powershell script details
                mem_data = makeapirequest(
                    ENDPOINT + "/" + data.get("value").get("id"), token, q_param
                )
                mem_id = data.get("value").get("id")
                # Remove keys before using DeepDiff
                mem_data = remove_keys(mem_data)
                mem_data.pop("deviceHealthScriptType", None)
                repo_data.pop("deviceHealthScriptType", None)

                # Check if script data is saved and read the file
                fname = filename.split(".")[0]
                # Get id from filename if there is any
                fname_id = filename.split("__")
                if len(fname_id) > 1:
                    fname_id = fname_id[1].replace(".json", "").replace(".yaml", "")
                else:
                    fname_id = ""
                # Get all remediation scripts and detection scripts files
                script_files = os.listdir(f"{configpath}/Script Data")
                # Filter out files that matches the id
                script_files = [f for f in script_files if fname_id in f]
                detection_script_name = ""
                remediation_script_name = ""
                # Set detection and remediation script name and path
                for f in script_files:
                    if "DetectionScript" in f:
                        detection_script_name = f"{configpath}/Script Data/{f}"
                    elif "RemediationScript" in f:
                        remediation_script_name = f"{configpath}/Script Data/{f}"

                if os.path.exists(detection_script_name) and os.path.exists(
                    remediation_script_name
                ):
                    with open(detection_script_name, "r", encoding="utf-8") as df:
                        repo_detection_config = df.read()
                    with open(remediation_script_name, "r", encoding="utf-8") as rf:
                        repo_remediation_config = rf.read()

                    mem_detection_config = base64.b64decode(
                        mem_data["detectionScriptContent"]
                    ).decode("utf-8")
                    mem_remediation_config = base64.b64decode(
                        mem_data["remediationScriptContent"]
                    ).decode("utf-8")

                    ddiff = DeepDiff(
                        mem_detection_config,
                        repo_detection_config,
                        ignore_order=True,
                    ).get("values_changed", {})
                    rdiff = DeepDiff(
                        mem_remediation_config,
                        repo_remediation_config,
                        ignore_order=True,
                    ).get("values_changed", {})
                    cdiff = DeepDiff(
                        mem_data,
                        repo_data,
                        ignore_order=True,
                        exclude_paths=[
                            "root['detectionScriptContent']",
                            "root['remediationScriptContent']",
                        ],
                    ).get("values_changed", {})

                    # If any changed values are found, push them to Intune
                    if cdiff or ddiff or rdiff and report is False:
                        detection_bytes = repo_detection_config.encode("utf-8")
                        remediation_bytes = repo_remediation_config.encode("utf-8")
                        repo_data["detectionScriptContent"] = base64.b64encode(
                            detection_bytes
                        ).decode("utf-8")
                        repo_data["remediationScriptContent"] = base64.b64encode(
                            remediation_bytes
                        ).decode("utf-8")
                        request_data = json.dumps(repo_data)
                        q_param = None
                        makeapirequestPatch(
                            ENDPOINT + "/" + mem_id, token, q_param, request_data
                        )

                    diff_config = DiffSummary(
                        data=cdiff,
                        name=repo_data["displayName"],
                        type="Proactive Remediation",
                    )

                    diff_detection = DiffSummary(
                        data=ddiff,
                        name="",
                        type="Detection Script",
                        message="Detection script changed, check commit history for change details",
                        notify=False,
                    )

                    diff_remediation = DiffSummary(
                        data=rdiff,
                        name="",
                        type="Remediation Script",
                        message="Remediation script changed, check commit history for change details",
                        notify=False,
                    )

                    diff_config.diffs += diff_detection.diffs + diff_remediation.diffs
                    diff_config.count += diff_detection.count + diff_remediation.count

                    diff_summary.append(diff_config)

                else:
                    print(f"Detection or Remediation script not found for {fname}")

                if assignment:
                    mem_assign_obj = get_object_assignment(mem_id, mem_assignments)
                    assignment_update = update_assignment(
                        assign_obj, mem_assign_obj, token, create_groups
                    )
                    if assignment_update is not None:
                        request_data = {
                            "deviceHealthScriptAssignments": assignment_update
                        }
                        post_assignment_update(
                            request_data,
                            mem_id,
                            "deviceManagement/deviceHealthScripts",
                            "assign",
                            token,
                        )

            # If remediation script does not exist, create it
            # and assign
            else:
                print("-" * 90)
                print(
                    "Proactive Remediation not found, creating: "
                    + repo_data["displayName"]
                )
                if report is False:
                    request_json = json.dumps(repo_data)
                    post_request = makeapirequestPost(
                        ENDPOINT,
                        token,
                        q_param=None,
                        jdata=request_json,
                        status_code=201,
                    )
                    mem_assign_obj = []
                    assignment = update_assignment(
                        assign_obj, mem_assign_obj, token, create_groups
                    )
                    if assignment is not None:
                        request_data = {"deviceHealthScriptAssignments": assignment}
                        post_assignment_update(
                            request_data,
                            post_request["id"],
                            "deviceManagement/deviceHealthScripts",
                            "assign",
                            token,
                        )
                    print(
                        "Proactive Remediation created with id: " + post_request["id"]
                    )

        # If any Proactive Remediations are left in mem_proactiveRemediation, remove them from Intune as they are not in the repo
        if mem_proactiveRemediation.get("value", None) is not None and remove is True:
            for val in mem_proactiveRemediation["value"]:
                if val.get("publisher", None) != "Microsoft":
                    print("-" * 90)
                    print(
                        "Removing Proactive Remediation from Intune: "
                        + val["displayName"]
                    )
                    if report is False:
                        makeapirequestDelete(
                            f"{ENDPOINT}/{val['id']}", token, status_code=200
                        )

    return diff_summary
