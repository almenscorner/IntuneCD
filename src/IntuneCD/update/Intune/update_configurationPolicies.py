#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Settings Catalog assignments in Intune,
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
    makeapirequestPost,
    makeapirequestPut,
)
from ...intunecdlib.load_file import load_file
from ...intunecdlib.process_scope_tags import get_scope_tags_id
from .update_assignment import post_assignment_update, update_assignment

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/configurationPolicies"


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
    This function updates all Settings Catalog configurations in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_summary = []
    # Set Settings Catalog path
    configpath = path + "/" + "Settings Catalog/"

    if os.path.exists(configpath):
        # Get configurations policies
        mem_data = makeapirequest(ENDPOINT, token)
        # Get current assignments
        mem_assignments = batch_assignment(
            mem_data, "deviceManagement/configurationPolicies/", "/assignments", token
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
                    if (
                        repo_data["name"] == val["name"]
                        and repo_data["technologies"] == val["technologies"]
                    ):
                        data["value"] = val
                        mem_data["value"].remove(val)

            if (
                "templateReference" in repo_data
                and repo_data["templateReference"].get("templateDisplayName")
                == "Endpoint detection and response"
            ):
                print("-" * 90)
                print(
                    f'Skipping "{repo_data["name"]}", Endpoint detection and response is currently not supported...',
                )
                continue

            # If Filter exists, continue
            if data["value"]:
                print("-" * 90)
                # Get Filter data from Intune
                mem_policy_data = makeapirequest(
                    ENDPOINT + "/" + data.get("value").get("id"), token
                )
                # Get Filter settings from Intune
                mem_policy_settings = makeapirequest(
                    ENDPOINT + "/" + data.get("value").get("id") + "/settings",
                    token,
                )
                # Add settings to the data dictionary
                mem_policy_data["settings"] = mem_policy_settings["value"]

                diff = DeepDiff(mem_policy_data, repo_data, ignore_order=True).get(
                    "values_changed", {}
                )

                # If any changed values are found, push them to Intune
                if diff and report is False:
                    request_data = json.dumps(repo_data)
                    q_param = None
                    makeapirequestPut(
                        ENDPOINT + "/" + data.get("value").get("id"),
                        token,
                        q_param,
                        request_data,
                        status_code=204,
                    )

                diff_policy = DiffSummary(
                    data=diff,
                    name=repo_data["name"],
                    type="Settings Catalog policy",
                )

                diff_summary.append(diff_policy)

                if assignment:
                    mem_assign_obj = get_object_assignment(
                        data.get("value").get("id"), mem_assignments
                    )
                    assignment_update = update_assignment(
                        assign_obj, mem_assign_obj, token, create_groups
                    )
                    if assignment_update is not None:
                        request_data = {"assignments": assignment_update}
                        post_assignment_update(
                            request_data,
                            data.get("value").get("id"),
                            "deviceManagement/configurationPolicies",
                            "assign",
                            token,
                        )

            # If Configuration Policy does not exist, create it and assign
            else:
                print("-" * 90)
                print(
                    "Configuration Policy not found, creating Policy: "
                    + repo_data["name"]
                )
                if report is False:
                    repo_data.pop("settingCount", None)
                    repo_data.pop("creationSource", None)
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
                            "deviceManagement/configurationPolicies",
                            "assign",
                            token,
                        )
                    print("Configuration Policy created with id: " + post_request["id"])

        # If any Configuration Policies are left in mem_data, remove them from Intune as they are not in the repo
        if mem_data.get("value", None) is not None and remove is True:
            for val in mem_data["value"]:
                print("-" * 90)
                print("Removing Configuration Policy from Intune: " + val["name"])
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}", token, status_code=200
                    )

    return diff_summary
