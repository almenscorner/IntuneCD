#!/usr/bin/env python3

"""
This module is used to update all Windows Quality Update Profiles in Intune.
"""

import json
import os

from deepdiff import DeepDiff
from .graph_request import (
    makeapirequest,
    makeapirequestPatch,
    makeapirequestPost,
    makeapirequestDelete,
)
from .graph_batch import batch_assignment, get_object_assignment
from .update_assignment import update_assignment, post_assignment_update
from .check_file import check_file
from .load_file import load_file
from .remove_keys import remove_keys
from .diff_summary import DiffSummary

# Set MS Graph endpoint
ENDPOINT = (
    "https://graph.microsoft.com/beta/deviceManagement/windowsQualityUpdateProfiles"
)


def update(
    path, token, assignment=False, report=False, create_groups=False, remove=False
):
    """
    This function updates all Windows Quality Update Profiles in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_summary = []
    # Set Windows Quality Update Profile path
    configpath = path + "/" + "Quality Updates"
    # If Windows Quality Update Profile path exists, continue
    if os.path.exists(configpath):
        # Get Quality Update profiles
        mem_data = makeapirequest(ENDPOINT, token)
        # Get current assignment
        mem_assignments = batch_assignment(
            mem_data,
            "deviceManagement/windowsQualityUpdateProfiles/",
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
                            mem_data["value"].remove(val)

                # If Windows Quality Update Profile exists, continue
                if data["value"]:
                    print("-" * 90)
                    mem_id = data["value"]["id"]
                    # Remove keys before using DeepDiff
                    data["value"] = remove_keys(data["value"])
                    data["value"].pop("deployableContentDisplayName", None)
                    data["value"].pop("releaseDateDisplayName", None)

                    diff = DeepDiff(data["value"], repo_data, ignore_order=True).get(
                        "values_changed", {}
                    )
                    rdiff = DeepDiff(
                        data["value"]["expeditedUpdateSettings"],
                        repo_data["expeditedUpdateSettings"],
                        ignore_order=True,
                    ).get("type_changes", {})

                    diff.update(rdiff)

                    # If any changed values are found, push them to Intune
                    if diff and report is False:
                        repo_data.pop("deployableContentDisplayName", None)
                        repo_data.pop("releaseDateDisplayName", None)
                        request_data = json.dumps(repo_data)
                        q_param = None
                        makeapirequestPatch(
                            ENDPOINT + "/" + mem_id, token, q_param, request_data
                        )

                    diff_profile = DiffSummary(
                        data=diff,
                        name=repo_data["displayName"],
                        type="Windows Quality Update Profile",
                    )

                    diff_summary.append(diff_profile)

                    if assignment:
                        mem_assign_obj = get_object_assignment(mem_id, mem_assignments)
                        update = update_assignment(
                            assign_obj, mem_assign_obj, token, create_groups
                        )
                        if update is not None:
                            request_data = {"assignments": update}
                            post_assignment_update(
                                request_data,
                                mem_id,
                                "deviceManagement/windowsQualityUpdateProfiles",
                                "assign",
                                token,
                                status_code=200,
                            )

                # If Quality Update profile does not exist, create it and assign
                else:
                    print("-" * 90)
                    print(
                        "Quality Update profile not found, creating profile: "
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
                            request_data = {"assignments": assignment}
                            post_assignment_update(
                                request_data,
                                post_request["id"],
                                "deviceManagement/windowsQualityUpdateProfiles",
                                "assign",
                                token,
                                status_code=200,
                            )
                        print(
                            "Quality Update profile created with id: "
                            + post_request["id"]
                        )

        # If any Windows Quality Update Profile are left in mem_data, remove them from Intune as they are not in the repo
        if mem_data.get("value", None) is not None and remove is True:
            for val in mem_data["value"]:
                print("-" * 90)
                print(
                    "Removing Quality Update Profile from Intune: " + val["displayName"]
                )
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}", token, status_code=200
                    )

    return diff_summary
