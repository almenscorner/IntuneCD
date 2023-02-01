#!/usr/bin/env python3

"""
This module updates Enrollment Configurations in Intune.
"""

import json
import os
import re

from deepdiff import DeepDiff
from .graph_request import makeapirequest, makeapirequestPatch, makeapirequestPost
from .check_file import check_file
from .load_file import load_file
from .remove_keys import remove_keys
from .graph_batch import batch_assignment, get_object_assignment
from .update_assignment import update_assignment, post_assignment_update
from .diff_summary import DiffSummary

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceEnrollmentConfigurations"


def update(path, token, assignment=False, report=False):
    """_summary_

    Args:
        path (str): Path to where the backup is saved
        token (str): Token to use for authenticating the request
        assignment (bool, optional): Decides if assignment should be updated. Defaults to False.
        report (bool, optional): If true, runs in report mode only. Defaults to False.
    """

    diff_summary = []
    # Set Enrollment Configuration path
    configpath = path + "/" + "Enrollment Configurations/"
    # If Enrollment Configuration path exists, continue
    if os.path.exists(configpath):

        # Get Enrollment Configurations
        intune_data = makeapirequest(ENDPOINT, token)

        # Get current assignments
        mem_assignments = batch_assignment(
            intune_data,
            "deviceManagement/deviceEnrollmentConfigurations/",
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

                config_type = repo_data.get("deviceEnrollmentConfigurationType", None)
                config_type = config_type[0].upper() + config_type[1:]
                config_type = re.findall("[A-Z][^A-Z]*", config_type)
                config_type = " ".join(config_type)

                data = {"value": ""}
                if intune_data["value"]:
                    for val in intune_data["value"]:
                        if val["@odata.type"] == "#microsoft.graph.windows10EnrollmentCompletionPageConfiguration":
                            continue
                        if repo_data["@odata.type"] == "#microsoft.graph.deviceEnrollmentPlatformRestrictionConfiguration":
                            if (
                                repo_data["@odata.type"] == val["@odata.type"]
                                and repo_data["displayName"] == val["displayName"]
                                and repo_data["platformType"] == val["platformType"]
                            ):
                                data["value"] = val
                        else:
                            if (
                                repo_data["@odata.type"] == val["@odata.type"]
                                and repo_data["displayName"] == val["displayName"]
                            ):
                                data["value"] = val

                # If Enrollment Configuration exists, continue
                if data["value"]:
                    print("-" * 90)
                    # Get Enrollment Configuration data from Intune
                    mem_id = data["value"]["id"]
                    mem_priority = data["value"]["priority"]
                    repo_priority = repo_data["priority"]
                    # Remove keys from data that should not be compared
                    data["value"] = remove_keys(data["value"])

                    if repo_priority != mem_priority and mem_priority != 0:
                        print(f"Updating Enrollment Config {config_type} Priority: " + repo_data["displayName"])
                        # Update Enrollment Configuration
                        if report is False:
                            request_data = json.dumps({"priority": repo_priority})
                            makeapirequestPost(
                                f"{ENDPOINT}/{mem_id}/setpriority", token, q_param=None, jdata=request_data, status_code=200
                            )

                    # Compare data from Intune with data from file
                    repo_data.pop("priority", None)
                    data["value"].pop("priority", None)
                    diff = DeepDiff(data["value"], repo_data, ignore_order=True).get("values_changed", {})

                    # If data differs, continue
                    if diff and report is False:
                        # Update Enrollment Configuration
                        repo_data.pop("priority", None)
                        repo_data.pop("deviceEnrollmentConfigurationType", None)
                        repo_data.pop("platformType", None)
                        request_data = json.dumps(repo_data)
                        makeapirequestPatch(ENDPOINT + "/" + mem_id, token, q_param=None, jdata=request_data, status_code=200)

                    # Add diff to summary
                    diff_config = DiffSummary(
                        data=diff, name=repo_data["displayName"], type=f"Enrollment Config {config_type}"
                    )
                    diff_summary.append(diff_config)

                    if assignment:
                        mem_assign_obj = get_object_assignment(mem_id, mem_assignments)
                        update = update_assignment(assign_obj, mem_assign_obj, token)
                        if update is not None:
                            request_data = {"enrollmentConfigurationAssignments": update}
                            post_assignment_update(
                                request_data,
                                mem_id,
                                "deviceManagement/deviceEnrollmentConfigurations",
                                "assign",
                                token,
                            )

                # If Enrollment Configuration does not exist, continue
                else:
                    print("-" * 90)
                    print(f"Creating Enrollment Config {config_type}: " + repo_data["displayName"])
                    # Create Enrollment Configuration
                    if report is False:
                        platform_types = ["android", "androidForWork"]

                        if repo_data["@odata.type"] == "#microsoft.graph.deviceEnrollmentPlatformRestrictionConfiguration":
                            if repo_data["platformType"] in platform_types:
                                for platform in platform_types:
                                    repo_data["platformType"] = platform
                                    request_data = json.dumps(repo_data)
                                    post_request = makeapirequestPost(
                                        ENDPOINT, token, q_param=None, jdata=request_data, status_code=201
                                    )
                            else:
                                request_data = json.dumps(repo_data)
                                post_request = makeapirequestPost(
                                    ENDPOINT, token, q_param=None, jdata=request_data, status_code=201
                                )
                        else:
                            request_data = json.dumps(repo_data)
                            post_request = makeapirequestPost(
                                ENDPOINT, token, q_param=None, jdata=request_data, status_code=201
                            )

                        mem_assign_obj = []
                        assignment = update_assignment(assign_obj, mem_assign_obj, token)
                        if assignment is not None:
                            request_data = {"enrollmentConfigurationAssignments": assignment}
                            post_assignment_update(
                                request_data,
                                post_request["id"],
                                "deviceManagement/deviceEnrollmentConfigurations",
                                "assign",
                                token,
                            )
                        print(f"Enrollment Config {config_type} created with id: " + post_request["id"])

    return diff_summary