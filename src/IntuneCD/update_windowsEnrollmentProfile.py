#!/usr/bin/env python3

"""
This module is used to update all Windows Enrollment Profiles in Intune.
"""

import json
import os

from deepdiff import DeepDiff
from .graph_request import makeapirequest, makeapirequestPatch, makeapirequestPost
from .graph_batch import batch_assignment, get_object_assignment
from .update_assignment import update_assignment, post_assignment_update
from .check_file import check_file
from .load_file import load_file
from .remove_keys import remove_keys
from .diff_summary import DiffSummary

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/windowsAutopilotDeploymentProfiles"


def update(path, token, assignment=False, report=False):
    """
    This function updates all Windows Enrollment Profiles in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_summary = []
    # Set Windows Enrollment Profile path
    configpath = path + "/" + "Enrollment Profiles/Windows"
    # If Windows Enrollment Profile path exists, continue
    if os.path.exists(configpath):
        # Get enrollment profiles
        mem_data = makeapirequest(ENDPOINT, token)
        # Get current assignment
        mem_assignments = batch_assignment(
            mem_data,
            "deviceManagement/windowsAutopilotDeploymentProfiles/",
            "/assignments",
            token,
        )

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            # Check which format the file is saved as then open file, load data
            # and set query parameter
            with open(file) as f:
                repo_data = load_file(filename, f)

                # Create object to pass in to assignment function
                assign_obj = {}
                if "assignments" in repo_data:
                    assign_obj = repo_data["assignments"]
                repo_data.pop("assignments", None)

                data = {"value": ""}
                if mem_data["value"]:
                    for val in mem_data["value"]:
                        if repo_data["displayName"] == val["displayName"]:
                            data["value"] = val

                # If Windows Enrollment Profile exists, continue
                if data["value"]:
                    print("-" * 90)
                    mem_id = data["value"]["id"]
                    # Remove keys before using DeepDiff
                    mem_data["value"][0] = remove_keys(mem_data["value"][0])

                    diff = DeepDiff(data["value"], repo_data, ignore_order=True).get(
                        "values_changed", {}
                    )

                    # If any changed values are found, push them to Intune
                    if diff and report is False:
                        if repo_data["managementServiceAppId"]:
                            pass
                        else:
                            repo_data["managementServiceAppId"] = ""
                        request_data = json.dumps(repo_data)
                        q_param = None
                        makeapirequestPatch(
                            ENDPOINT + "/" + mem_id, token, q_param, request_data
                        )

                    diff_profile = DiffSummary(
                        data=diff,
                        name=repo_data["displayName"],
                        type="Windows Enrollment Profile",
                    )

                    diff_summary.append(diff_profile)

                    if assignment:
                        mem_assign_obj = get_object_assignment(mem_id, mem_assignments)
                        update = update_assignment(assign_obj, mem_assign_obj, token)
                        if update is not None:
                            request_data = {"target": update}
                            post_assignment_update(
                                request_data,
                                mem_id,
                                "deviceManagement/windowsAutopilotDeploymentProfiles",
                                "assign",
                                token,
                                status_code=201,
                            )

                # If Autopilot profile does not exist, create it and assign
                else:
                    print("-" * 90)
                    print(
                        "Autopilot profile not found, creating profile: "
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
                            assign_obj, mem_assign_obj, token
                        )
                        if assignment is not None:
                            request_data = {"target": assignment[0]["target"]}
                            post_assignment_update(
                                request_data,
                                post_request["id"],
                                "deviceManagement/windowsAutopilotDeploymentProfiles",
                                "assignments",
                                token,
                                status_code=201,
                            )
                        print(
                            "Autopilot profile created with id: " + post_request["id"]
                        )

    return diff_summary
