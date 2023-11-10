#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Windows Enrollment Status Page Profiles in Intune.
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
from ...intunecdlib.remove_keys import remove_keys
from .update_assignment import post_assignment_update, update_assignment

# Set MS Graph endpoint
ENDPOINT = (
    "https://graph.microsoft.com/beta/deviceManagement/deviceEnrollmentConfigurations"
)
APP_ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"


def update(
    path, token, assignment=False, report=False, create_groups=False, remove=False
):
    """
    This function updates all Windows Enrollment Status Page Profiles in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_summary = []
    # Set Windows Enrollment Status Page Profile path
    configpath = path + "/" + "Enrollment Profiles/Windows/ESP/"
    # If Windows Enrollment Profile path exists, continue
    if os.path.exists(configpath):
        # Get enrollment profiles
        mem_data = makeapirequest(ENDPOINT, token)
        # Get current assignment
        mem_assignments = batch_assignment(
            mem_data,
            "deviceManagement/deviceEnrollmentConfigurations/",
            "/assignments",
            token,
        )

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            # Check which format the file is saved as then open file, load data and set query parameter
            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)

            # Create object to pass in to assignment function
            assign_obj = {}
            if "assignments" in repo_data:
                assign_obj = repo_data["assignments"]
            repo_data.pop("assignments", None)

            data = {"value": ""}
            if mem_data["value"]:
                for val in mem_data["value"]:
                    if (
                        repo_data["displayName"] == val["displayName"]
                        and repo_data["@odata.type"] == val["@odata.type"]
                    ):
                        data["value"] = val
                        mem_data["value"].remove(val)

            # If Enrollment Status Page Profile exists, continue
            if data["value"]:
                print("-" * 90)
                mem_id = data.get("value").get("id")
                # Remove keys before using DeepDiff
                mem_data["value"][0] = remove_keys(mem_data["value"][0])

                # Get application ID of configured apps
                if "selectedMobileAppNames" in repo_data:
                    app_ids = []

                    for app in repo_data["selectedMobileAppNames"]:
                        q_param = {
                            "$filter": f"(isof('{str(app['type']).replace('#','')}'))",
                            "$search": '"' + app["name"] + '"',
                        }

                        app_request = makeapirequest(APP_ENDPOINT, token, q_param)
                        if app_request["value"]:
                            app_ids.append(app_request["value"][0]["id"])
                        else:
                            print("No app found with name: " + app["name"])

                    if app_ids:
                        repo_data.pop("selectedMobileAppNames", None)
                        repo_data["selectedMobileAppIds"] = app_ids

                diff = DeepDiff(data["value"], repo_data, ignore_order=True).get(
                    "values_changed", {}
                )

                # If any changed values are found, push them to Intune
                if diff and report is False:
                    repo_data.pop("priority", None)

                    request_data = json.dumps(repo_data)
                    q_param = None
                    makeapirequestPatch(
                        f"{ENDPOINT}/{mem_id}", token, q_param, request_data
                    )

                diff_profile = DiffSummary(
                    data=diff,
                    name=repo_data["displayName"],
                    type="Enrollment Status Page Profile",
                )

                diff_summary.append(diff_profile)

                if assignment:
                    mem_assign_obj = get_object_assignment(mem_id, mem_assignments)
                    assignment_update = update_assignment(
                        assign_obj, mem_assign_obj, token, create_groups
                    )
                    if assignment_update is not None:
                        target = [{"target": t["target"]} for t in assignment_update]
                        request_data = {"enrollmentConfigurationAssignments": target}
                        post_assignment_update(
                            request_data,
                            mem_id,
                            "deviceManagement/deviceEnrollmentConfigurations",
                            "assign",
                            token,
                            status_code=200,
                        )

            # If Enrollmen Status Page profile does not exist, create it and assign
            else:
                print("-" * 90)
                print(
                    "Enrollment Status Page profile not found, creating profile: "
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
                        assignments = []
                        for assign in assignment:
                            assignments.append({"target": assign["target"]})
                        request_data = {
                            "enrollmentConfigurationAssignments": assignments
                        }

                        post_assignment_update(
                            request_data,
                            post_request["id"],
                            "deviceManagement/deviceEnrollmentConfigurations",
                            "assign",
                            token,
                            status_code=200,
                        )
                    print(
                        "Enrollment Status Page profile created with id: "
                        + post_request["id"]
                    )

        # If any ESP are left in mem_data, remove them from Intune as they are not in the repo
        if mem_data.get("value", None) is not None and remove is True:
            for val in mem_data["value"]:
                if val["displayName"] == "All users and all devices":
                    continue
                if (
                    val["@odata.type"]
                    == "#microsoft.graph.windowsEnrollmentStatusPageConfiguration"
                ):
                    print("-" * 90)
                    print(
                        "Removing Enrollment Status Page profile from Intune: "
                        + val["displayName"]
                    )
                    if report is False:
                        makeapirequestDelete(
                            f"{ENDPOINT}/{val['id']}", token, status_code=200
                        )

    return diff_summary
