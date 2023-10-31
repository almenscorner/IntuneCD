#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Compliance Policies in Intune.
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
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceCompliancePolicies"


def update(
    path, token, assignment=False, report=False, create_groups=False, remove=False
):
    """
    This function updates all Compliance Polices in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    # Set Compliance Policy path
    configpath = path + "/" + "Compliance Policies/Policies/"
    diff_summary = []
    # If App Configuration path exists, continue
    if os.path.exists(configpath):
        # Get compliance policies
        q_param = {
            "expand": "scheduledActionsForRule($expand=scheduledActionConfigurations)"
        }
        mem_data = makeapirequest(ENDPOINT, token, q_param)
        # Get current assignments
        mem_assignments = batch_assignment(
            mem_data,
            "deviceManagement/deviceCompliancePolicies/",
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

            # If Compliance Policy exists, continue
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
                data["value"] = remove_keys(data["value"])

                if data.get("value", {}).get("scheduledActionsForRule"):
                    for rule in data.get("value").get("scheduledActionsForRule"):
                        remove_keys(rule)
                    for scheduled_config in (
                        data.get("value")
                        .get("scheduledActionsForRule", [])[0]
                        .get("scheduledActionConfigurations", [])
                    ):
                        remove_keys(scheduled_config)

                diff = DeepDiff(
                    data["value"],
                    repo_data,
                    ignore_order=True,
                    exclude_paths="root['scheduledActionsForRule'][0]['scheduledActionConfigurations']",
                ).get("values_changed", {})

                # If any changed values are found, push them to Intune
                if diff and report is False:
                    scheduled_actions = repo_data["scheduledActionsForRule"]
                    repo_data.pop("scheduledActionsForRule", None)
                    request_data = json.dumps(repo_data)
                    q_param = None
                    makeapirequestPatch(
                        ENDPOINT + "/" + mem_id,
                        token,
                        q_param,
                        request_data,
                        status_code=204,
                    )
                    repo_data["scheduledActionsForRule"] = scheduled_actions

                diff_policy = DiffSummary(
                    data=diff,
                    name=repo_data["displayName"],
                    type="Compliance Policy",
                )

                diff_summary.append(diff_policy)

                if repo_data["scheduledActionsForRule"]:
                    for mem_rule, repo_rule in zip(
                        data.get("value").get("scheduledActionsForRule"),
                        repo_data["scheduledActionsForRule"],
                    ):
                        rdiff = DeepDiff(mem_rule, repo_rule, ignore_order=True).get(
                            "values_changed", {}
                        )

                    if rdiff and report is False:
                        request_data = {
                            "deviceComplianceScheduledActionForRules": [
                                {
                                    "ruleName": "PasswordRequired",
                                    "scheduledActionConfigurations": repo_data[
                                        "scheduledActionsForRule"
                                    ][0]["scheduledActionConfigurations"],
                                }
                            ]
                        }

                        request_json = json.dumps(request_data)
                        q_param = None
                        makeapirequestPost(
                            ENDPOINT + "/" + mem_id + "/scheduleActionsForRules",
                            token,
                            q_param,
                            request_json,
                        )

                    rdiff_summary = DiffSummary(
                        data=rdiff,
                        name="",
                        type="Compliance Policy Rules",
                    )

                    diff_policy.diffs += rdiff_summary.diffs
                    diff_policy.count += rdiff_summary.count

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
                            "deviceManagement/deviceCompliancePolicies",
                            "assign",
                            token,
                        )

            # If Compliance Policy does not exist, create it and assign
            else:
                print("-" * 90)
                print(
                    "Compliance Policy not found, creating Policy: "
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
                            "deviceManagement/deviceCompliancePolicies",
                            "assign",
                            token,
                        )
                    print("Compliance Policy created with id: " + post_request["id"])

        # If any Compliance Policies are left in mem_data, remove them from Intune as they are not in the repo
        if mem_data.get("value", None) is not None and remove is True:
            for val in mem_data["value"]:
                print("-" * 90)
                print("Removing Compliance Policy from Intune: " + val["displayName"])
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}", token, status_code=200
                    )

    return diff_summary
