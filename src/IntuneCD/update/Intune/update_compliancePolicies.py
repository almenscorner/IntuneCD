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
    makeapirequestPut,
)
from ...intunecdlib.load_file import load_file
from ...intunecdlib.process_scope_tags import get_scope_tags_id
from ...intunecdlib.remove_keys import remove_keys
from .update_assignment import post_assignment_update, update_assignment

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/compliancePolicies"


def _remove_keys(data):
    if isinstance(data, dict):
        return {
            k: _remove_keys(v)
            for k, v in data.items()
            if k
            not in [
                "settingValueTemplateReference",
                "settingInstanceTemplateReference",
                "note",
                "settingCount",
                "creationSource",
                "settings@odata.context",
                "detectionScriptName",
            ]
        }
    if isinstance(data, list):
        return [_remove_keys(v) for v in data]

    return data


def _get_detection_script_id_path(data, path=None):
    if path is None:
        path = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                new_path = _get_detection_script_id_path(v, path + [k])
                if new_path is not None:
                    return new_path
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    new_path = _get_detection_script_id_path(item, path + [k, i])
                    if new_path is not None:
                        return new_path
            elif v == "linux_customcompliance_discoveryscript":
                return path
    return None


def _set_value_from_path(data, value, path):
    item = data
    for key in path[:-1]:
        if isinstance(item, list):
            item = item[int(key)]
        else:
            item = item[key]
    if isinstance(item, list):
        item[int(path[-1])] = value
    else:
        item[path[-1]] = value
    return data


def _set_detection_script_id(data, token):
    # get detection script id
    script_id = makeapirequest(
        "https://graph.microsoft.com/beta/deviceManagement/reusablePolicySettings/",
        token,
        {"$filter": f"displayName eq '{data['detectionScriptName']}'"},
    )
    if script_id.get("value"):
        script_id_path = _get_detection_script_id_path(data)
        script_id_path = script_id_path + ["simpleSettingValue", "value"]
        data = _set_value_from_path(data, script_id["value"][0]["id"], script_id_path)

    return data


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
        q_param = {"$expand": "settings"}
        mem_data = makeapirequest(ENDPOINT, token, q_param)
        # Get current assignments
        mem_assignments = batch_assignment(
            mem_data,
            "deviceManagement/compliancePolicies/",
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

            # continue to next file if not "technologies" in repo_data
            if "technologies" not in repo_data:
                continue

            # Create object to pass in to assignment function
            assign_obj = {}
            if "assignments" in repo_data:
                assign_obj = repo_data["assignments"]
            repo_data.pop("assignments", None)

            if scope_tags:
                repo_data = get_scope_tags_id(repo_data, scope_tags)

            # If Compliance Policy exists, continue
            data = {"value": ""}
            if mem_data["value"]:
                for val in mem_data["value"]:
                    if (
                        repo_data["technologies"] == val["technologies"]
                        and repo_data["name"] == val["name"]
                    ):
                        data["value"] = val
                        mem_data["value"].remove(val)

            if data["value"]:
                print("-" * 90)
                mem_id = data.get("value", {}).get("id", None)
                data["value"] = remove_keys(data["value"])

                scheduledActionsForRule = makeapirequest(
                    f"{ENDPOINT}/{mem_id}/scheduledActionsForRule",
                    token,
                    {"$expand": "scheduledActionConfigurations"},
                )

                data.get("value")["scheduledActionsForRule"] = scheduledActionsForRule[
                    "value"
                ]

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
                    exclude_paths=[
                        "root['scheduledActionsForRule'][0]['scheduledActionConfigurations']",
                        "root['settings']",
                        "root['settings@odata.context']",
                    ],
                ).get("values_changed", {})

                # If any changed values are found, push them to Intune
                if diff and report is False:
                    if repo_data.get("detectionScriptName"):
                        repo_data = _set_detection_script_id(repo_data, token)
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
                    name=repo_data["name"],
                    type="Compliance Policy",
                )

                diff_summary.append(diff_policy)

                if repo_data["scheduledActionsForRule"]:
                    rdiff = None
                    for mem_rule, repo_rule in zip(
                        data.get("value").get("scheduledActionsForRule"),
                        repo_data["scheduledActionsForRule"],
                    ):
                        rdiff = DeepDiff(mem_rule, repo_rule, ignore_order=True).get(
                            "values_changed", {}
                        )

                    if rdiff and report is False:
                        request_data = {
                            "scheduledActions": repo_data["scheduledActionsForRule"]
                        }

                        request_json = json.dumps(request_data)
                        q_param = None
                        makeapirequestPost(
                            f"{ENDPOINT}/{mem_id}/setScheduledActions/",
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

                if repo_data.get("settings"):
                    for repo_setting, mem_setting in zip(
                        repo_data.get("settings"), data["value"].get("settings")
                    ):
                        if (
                            "custom"
                            not in repo_setting["settingInstance"][
                                "settingDefinitionId"
                            ]
                        ):
                            sdiff = DeepDiff(
                                mem_setting, repo_setting, ignore_order=True
                            ).get("values_changed", {})

                            if sdiff and report is False:
                                request_json = json.dumps(repo_data)
                                q_param = None
                                makeapirequestPut(
                                    f"{ENDPOINT}/{mem_id}",
                                    token,
                                    q_param,
                                    request_json,
                                    status_code=204,
                                )

                                sdiff_summary = DiffSummary(
                                    data=sdiff,
                                    name="",
                                    type="Compliance Policy Settings",
                                )

                                diff_policy.diffs += sdiff_summary.diffs
                                diff_policy.count += sdiff_summary.count

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
                            "deviceManagement/compliancePolicies",
                            "assign",
                            token,
                        )

            # If Compliance Policy does not exist, create it and assign
            else:
                print("-" * 90)
                print(
                    "Compliance Policy not found, creating Policy: " + repo_data["name"]
                )
                if report is False:
                    if repo_data.get("detectionScriptName"):
                        repo_data = _set_detection_script_id(repo_data, token)
                    repo_data = _remove_keys(repo_data)
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

                    request_data = {
                        "scheduledActions": repo_data["scheduledActionsForRule"]
                    }

                    request_json = json.dumps(request_data)
                    q_param = None
                    makeapirequestPost(
                        f"{ENDPOINT}/{post_request['id']}/setScheduledActions/",
                        token,
                        q_param,
                        request_json,
                    )

                    if assignment is not None:
                        request_data = {"assignments": assignment}
                        post_assignment_update(
                            request_data,
                            post_request["id"],
                            "deviceManagement/compliancePolicies",
                            "assign",
                            token,
                        )
                    print("Compliance Policy created with id: " + post_request["id"])

        # If any Compliance Policies are left in mem_data, remove them from Intune as they are not in the repo
        if mem_data.get("value", None) is not None and remove is True:
            for val in mem_data["value"]:
                print("-" * 90)
                print("Removing Compliance Policy from Intune: " + val["name"])
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}", token, status_code=200
                    )

    return diff_summary
