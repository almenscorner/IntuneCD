#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all App Configuration Assignments in Intune.
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
from ...intunecdlib.process_scope_tags import get_scope_tags_id
from ...intunecdlib.remove_keys import remove_keys
from .update_assignment import post_assignment_update, update_assignment

# Set MS Graph endpoint
ENDPOINT = (
    "https://graph.microsoft.com/beta/deviceAppManagement/mobileAppConfigurations"
)
APP_ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"


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
    This function updates all App Configuration Polices in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_summary = []
    # Set App Configuration path
    configpath = path + "/" + "App Configuration/"
    # If App Configuration path exists, continue
    if os.path.exists(configpath):
        # Get App Configurations
        mem_data = makeapirequest(ENDPOINT, token)
        # Get current assignments
        mem_assignments = batch_assignment(
            mem_data,
            "deviceAppManagement/mobileAppConfigurations/",
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

            # Get scope tag ID
            if scope_tags:
                repo_data = get_scope_tags_id(repo_data, scope_tags)

            # If App Configuration exists, continue
            data = {"value": ""}
            if mem_data["value"]:
                for val in mem_data["value"]:
                    if (
                        repo_data["@odata.type"] == val["@odata.type"]
                        and repo_data["displayName"] == val["displayName"]
                    ):
                        data["value"] = val
                        mem_data["value"].remove(val)

            if data["value"]:
                print("-" * 90)
                mem_id = data.get("value", {}).get("id", None)
                # Remove keys before using DeepDiff
                data = remove_keys(data)
                repo_data.pop("targetedMobileApps", None)

                if repo_data.get("payloadJson"):
                    repo_data["payloadJson"] = base64.b64encode(
                        json.dumps(repo_data["payloadJson"]).encode("utf-8")
                    ).decode("utf-8")

                diff = DeepDiff(data["value"], repo_data, ignore_order=True).get(
                    "values_changed", {}
                )

                # If any changed values are found, push them to Intune
                if diff and report is False:
                    request_data = json.dumps(repo_data)
                    q_param = None
                    makeapirequestPatch(
                        ENDPOINT + "/" + mem_id,
                        token,
                        q_param,
                        request_data,
                        status_code=204,
                    )

                diff_config = DiffSummary(
                    data=diff,
                    name=repo_data["displayName"],
                    type="App Configuration",
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
                            "deviceAppManagement/mobileAppConfigurations/",
                            "/microsoft.graph.managedDeviceMobileAppConfiguration/assign",
                            token,
                        )

            # If App Configuration does not exist, create it and assign
            else:
                print("-" * 90)
                print(
                    "App Configuration not found, creating: " + repo_data["displayName"]
                )

                if repo_data.get("payloadJson"):
                    repo_data["payloadJson"] = base64.b64encode(
                        json.dumps(repo_data["payloadJson"]).encode("utf-8")
                    ).decode("utf-8")

                app_ids = {}
                # If backup contains targeted apps, search for the app
                if repo_data["targetedMobileApps"]:
                    q_param = {
                        "$filter": "(isof("
                        + "'"
                        + str(repo_data["targetedMobileApps"]["type"]).replace("#", "")
                        + "'"
                        + "))",
                        "$search": f'"{repo_data["targetedMobileApps"]["appName"]}"',
                    }
                    app_request = makeapirequest(APP_ENDPOINT, token, q_param)
                    if app_request["value"]:
                        app_ids = app_request["value"][0]["id"]
                # If the app could be found and matches type and name in
                # backup, continue to create
                if app_ids and report is False:
                    repo_data.pop("targetedMobileApps")
                    repo_data["targetedMobileApps"] = [app_ids]
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
                            "deviceAppManagement/mobileAppConfigurations/",
                            "/microsoft.graph.managedDeviceMobileAppConfiguration/assign",
                            token,
                        )
                    print("App Configuration created with id: " + post_request["id"])
                else:
                    print(
                        "App configured in App Configuration profile could not be found, skipping creation"
                    )

        # If any App Configurations are left in mem_data, remove them from Intune as they are not in the repo
        if mem_data.get("value", None) is not None and remove is True:
            for val in mem_data["value"]:
                print("-" * 90)
                print("Removing App Configuration from Intune: " + val["displayName"])
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}", token, status_code=200
                    )

    return diff_summary
