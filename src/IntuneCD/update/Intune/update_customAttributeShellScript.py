#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Custom Attribute xss in Intune.
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
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceCustomAttributeShellScripts"
ASSIGNMENT_ENDPOINT = (
    "https://graph.microsoft.com/beta/deviceManagement/deviceManagementScripts"
)


def update(
    path, token, assignment=False, report=False, create_groups=False, remove=False
):
    """
    This function updates all Custom Attribute Shell scripts in Intune if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_summary = []
    # Set Custom Attribute Shell script path
    configpath = path + "/" + "Custom Attributes/"
    # If Custom Attribute Shell script path exists, continue
    if os.path.exists(configpath):
        # Get scripts
        mem_shellScript = makeapirequest(ENDPOINT, token)
        # Get current assignment
        mem_assignments = batch_assignment(
            mem_shellScript,
            "deviceManagement/deviceCustomAttributeShellScripts/",
            "?$expand=assignments",
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
            if mem_shellScript["value"]:
                for val in mem_shellScript["value"]:
                    if repo_data["displayName"] == val["displayName"]:
                        data["value"] = val
                        mem_shellScript["value"].remove(val)

            # If Custom Attribute Shell script exists, continue
            if data["value"]:
                print("-" * 90)
                q_param = None
                # Get Shell script details
                mem_data = makeapirequest(
                    ENDPOINT + "/" + data.get("value").get("id"), token
                )
                mem_id = mem_data["id"]
                # Remove keys before using DeepDiff
                mem_data = remove_keys(mem_data)
                name = repo_data["displayName"]
                keys_to_remove = [
                    "customAttributeName",
                    "displayName",
                    "customAttributeType",
                ]
                for key in keys_to_remove:
                    repo_data.pop(key, None)
                    mem_data.pop(key, None)

                # Check if script data is saved and read the file
                fname_id = filename.split("__")
                if len(fname_id) > 1:
                    fname_id = fname_id[1].replace(".json", "").replace(".yaml", "")
                else:
                    fname_id = ""
                script_files = os.listdir(configpath + "/Script Data/")
                script_file = [
                    x
                    for x in script_files
                    if fname_id in x or repo_data["fileName"] in x
                ]
                if script_file:
                    with open(
                        configpath + "/Script Data/" + script_file[0],
                        "r",
                        encoding="utf-8",
                    ) as f:
                        repo_payload_config = f.read()

                    mem_payload_config = base64.b64decode(
                        mem_data["scriptContent"]
                    ).decode("utf-8")

                    pdiff = DeepDiff(
                        mem_payload_config, repo_payload_config, ignore_order=True
                    ).get("values_changed", {})
                    cdiff = DeepDiff(
                        mem_data,
                        repo_data,
                        ignore_order=True,
                        exclude_paths="root['scriptContent']",
                    ).get("values_changed", {})

                    # If any changed values are found, push them to Intune
                    if pdiff or cdiff and report is False:
                        shell_bytes = repo_payload_config.encode("utf-8")
                        repo_data["scriptContent"] = base64.b64encode(
                            shell_bytes
                        ).decode("utf-8")
                        request_data = json.dumps(repo_data)
                        q_param = None
                        makeapirequestPatch(
                            ENDPOINT + "/" + mem_id, token, q_param, request_data
                        )

                    diff_config = DiffSummary(
                        data=cdiff,
                        name=name,
                        type="Custom Attribute",
                    )

                    diff_script = DiffSummary(
                        data=pdiff,
                        name="",
                        type="Custom Attribute Shell Script",
                        message="Script changed, check commit history for details",
                        notify=False,
                    )

                    diff_config.diffs += diff_script.diffs
                    diff_config.count += diff_script.count

                    diff_summary.append(diff_config)

                if assignment:
                    mem_assign_obj = get_object_assignment(mem_id, mem_assignments)
                    assignment_update = update_assignment(
                        assign_obj, mem_assign_obj, token, create_groups
                    )
                    if assignment_update is not None:
                        request_data = {
                            "deviceManagementScriptAssignments": assignment_update
                        }
                        post_assignment_update(
                            request_data,
                            mem_id,
                            "deviceManagement/deviceManagementScripts",
                            "assign",
                            token,
                        )

            # If Custom Attribute Shell script does not exist, create it and assign
            else:
                print("-" * 90)
                print(
                    "Custom Attribute not found, creating script: "
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
                        request_data = {"deviceManagementScriptAssignments": assignment}
                        post_assignment_update(
                            request_data,
                            post_request["id"],
                            "deviceManagement/deviceManagementScripts",
                            "assign",
                            token,
                        )
                    print("Custom Attribute created with id: " + post_request["id"])

        # If any Custom Attribute scripts are left in mem_shellScript, remove them from Intune as they are not in the repo
        if mem_shellScript.get("value", None) is not None and remove is True:
            for val in mem_shellScript["value"]:
                print("-" * 90)
                print("Removing Custom Attribute from Intune: " + val["displayName"])
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}", token, status_code=200
                    )

    return diff_summary
