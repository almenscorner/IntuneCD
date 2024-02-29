#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all App Protection Policies in Intune.
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
ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/"


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
    This function updates all App Protection Polices in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    # Set App Protection path
    configpath = path + "/" + "App Protection/"
    diff_summary = []
    # If App Configuration path exists, continue
    if os.path.exists(configpath):
        # Get App Protections
        mem_data = makeapirequest(f"{ENDPOINT}managedAppPolicies", token)
        # Get current assignments
        mem_assignments = batch_assignment(
            mem_data, "deviceAppManagement/", "/assignments", token, app_protection=True
        )

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            # Check which format the file is saved as then open file, load data
            # and set query parameter
            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)

            if repo_data:
                if (
                    repo_data["@odata.type"]
                    == "#microsoft.graph.mdmWindowsInformationProtectionPolicy"
                ):
                    platform = "mdmWindowsInformationProtectionPolicies"
                elif (
                    repo_data["@odata.type"]
                    == "#microsoft.graph.windowsInformationProtectionPolicy"
                ):
                    platform = "windowsInformationProtectionPolicies"
                else:
                    platform = f"{str(repo_data['@odata.type']).split('.')[2]}s"

            # Create object to pass in to assignment function
            assign_obj = {}
            if "assignments" in repo_data:
                assign_obj = repo_data["assignments"]
            repo_data.pop("assignments", None)

            # Get scope tag ID
            if scope_tags:
                repo_data = get_scope_tags_id(repo_data, scope_tags)

            # If App Protection exists, continue
            data = {"value": ""}
            if mem_data["value"]:
                for val in mem_data["value"]:
                    if (
                        "targetedAppManagementLevels" in val
                        and "targetedAppManagementLevels" in repo_data
                    ):
                        if (
                            repo_data["targetedAppManagementLevels"]
                            == val["targetedAppManagementLevels"]
                            and repo_data["displayName"] == val["displayName"]
                        ):
                            data["value"] = val
                            mem_data["value"].remove(val)
                    elif (
                        repo_data["@odata.type"] == val["@odata.type"]
                        and repo_data["displayName"] == val["displayName"]
                    ):
                        data["value"] = val
                        mem_data["value"].remove(val)

            if data["value"]:
                print("-" * 90)
                mem_id = data.get("value", {}).get("id", None)
                # Remove keys before using DeepDiff
                data["value"] = remove_keys(data["value"])

                diff = DeepDiff(data["value"], repo_data, ignore_order=True).get(
                    "values_changed", {}
                )

                if (
                    repo_data["@odata.type"]
                    == "#microsoft.graph.windowsInformationProtectionPolicy"
                ):
                    response_code = 200
                else:
                    response_code = 204

                # If any changed values are found, push them to Intune
                if diff and report is False:
                    request_data = json.dumps(repo_data)
                    q_param = None
                    makeapirequestPatch(
                        f"{ENDPOINT}{platform}/{mem_id}",
                        token,
                        q_param,
                        request_data,
                        status_code=response_code,
                    )

                diff_config = DiffSummary(
                    data=diff,
                    name=repo_data["displayName"],
                    type="App Protection",
                )
                diff_summary.append(diff_config)

                if assignment:
                    mem_assign_obj = get_object_assignment(mem_id, mem_assignments)
                    assignment_update = update_assignment(
                        assign_obj, mem_assign_obj, token, create_groups
                    )
                    if assignment_update is not None:
                        request_data = {"assignments": assignment_update}
                        post_assignment_update(
                            request_data,
                            mem_id,
                            f"deviceAppManagement/{platform}",
                            "assign",
                            token,
                            status_code=204,
                        )

            # If App Protection does not exist, create it and assign
            else:
                print("-" * 90)
                print(
                    "App Protection not found, creating policy: "
                    + repo_data["displayName"]
                )
                if report is False:
                    request_json = json.dumps(repo_data)
                    post_request = makeapirequestPost(
                        f"{ENDPOINT}managedAppPolicies",
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
                            f"deviceAppManagement/{platform}",
                            "assign",
                            token,
                            status_code=204,
                        )
                    print("App Protection created with id: " + post_request["id"])

        # If any App Protections are left in mem_data, remove them from Intune as they are not in the repo
        if mem_data.get("value", None) is not None and remove is True:
            for val in mem_data["value"]:
                print("-" * 90)
                print("Removing App Protection from Intune: " + val["displayName"])
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}managedAppPolicies/{val['id']}",
                        token,
                        status_code=204,
                    )

    return diff_summary
