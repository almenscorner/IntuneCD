#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Windows Enrollment Profiles in Intune.
"""

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
from ...intunecdlib.process_scope_tags import get_scope_tags_id
from ...intunecdlib.remove_keys import remove_keys
from .update_assignment import post_assignment_update, update_assignment

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/windowsAutopilotDeploymentProfiles"


def update(
    path,
    token,
    assignment=False,
    report=False,
    create_groups=False,
    remove=False,
    scope_tags=None,
):
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
            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)

            # Create object to pass in to assignment function
            assign_obj = {}
            if "assignments" in repo_data:
                assign_obj = repo_data["assignments"]
            repo_data.pop("assignments", None)

            if scope_tags:
                repo_data = get_scope_tags_id(repo_data, scope_tags)

            data = {"value": ""}
            if mem_data["value"]:
                for val in mem_data["value"]:
                    if repo_data["displayName"] == val["displayName"]:
                        data["value"] = val
                        mem_data["value"].remove(val)

            # If Windows Enrollment Profile exists, continue
            if data["value"]:
                print("-" * 90)
                mem_id = data.get("value").get("id")
                # Remove keys before using DeepDiff
                data["value"] = remove_keys(data["value"])

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
                    assignment_update = update_assignment(
                        assign_obj, mem_assign_obj, token, create_groups
                    )
                    if assignment_update is not None:
                        for target in assignment_update:
                            request_data = {"target": target["target"]}
                            post_assignment_update(
                                request_data,
                                mem_id,
                                "deviceManagement/windowsAutopilotDeploymentProfiles",
                                "assignments",
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
                        assign_obj, mem_assign_obj, token, create_groups
                    )
                    if assignment is not None:
                        for target in assignment:
                            request_data = {"target": target["target"]}
                            post_assignment_update(
                                request_data,
                                post_request["id"],
                                "deviceManagement/windowsAutopilotDeploymentProfiles",
                                "assignments",
                                token,
                                status_code=201,
                            )
                    print("Autopilot profile created with id: " + post_request["id"])

        # If any Windows Enrollment Profile are left in mem_data, remove them from Intune as they are not in the repo
        if mem_data.get("value", None) is not None and remove is True:
            for val in mem_data["value"]:
                print("-" * 90)
                print("Removing Autopilot Profile from Intune: " + val["displayName"])
                if report is False:
                    # Remove assignments so we can delete the profile
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}/assignments", token, status_code=200
                    )
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}", token, status_code=200
                    )

    return diff_summary
