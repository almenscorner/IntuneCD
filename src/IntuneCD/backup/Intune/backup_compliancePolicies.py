#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Compliance Polices in Intune.
"""

from ...intunecdlib.check_prefix import check_prefix_match
from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import batch_assignment, get_object_assignment
from ...intunecdlib.graph_request import makeapirequest, makeAuditRequest
from ...intunecdlib.process_audit_data import process_audit_data
from ...intunecdlib.process_scope_tags import get_scope_tags_name
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/compliancePolicies"


def _check_linux_discovery_script(data):
    if isinstance(data, dict):
        if "linux_customcompliance_discoveryscript" in data.values():
            return True
        return any(_check_linux_discovery_script(v) for v in data.values())
    if isinstance(data, list):
        return any(_check_linux_discovery_script(v) for v in data)
    return False


def _get_detection_script_id(data, path=None):
    if path is None:
        path = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                new_path = _get_detection_script_id(v, path + [k])
                if new_path is not None:
                    return new_path
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    new_path = _get_detection_script_id(item, path + [k, i])
                    if new_path is not None:
                        return new_path
            elif v == "linux_customcompliance_discoveryscript":
                return path
    return None


def _get_value_from_path(data, path):
    for key in path:
        if isinstance(data, list):
            data = data[int(key)]
        else:
            data = data[key]
    return data["simpleSettingValue"]["value"]


# Get all Compliance policies and save them in specified path
def savebackup(path, output, exclude, token, prefix, append_id, audit, scope_tags):
    """
    Saves all Compliance policies in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    audit_data = None
    configpath = path + "/" + "Compliance Policies/Policies/"
    q_param = {
        "$expand": "settings",
    }
    data = makeapirequest(ENDPOINT, token, q_param)

    assignment_responses = batch_assignment(
        data, "deviceManagement/compliancePolicies/", "/assignments", token
    )
    if audit:
        graph_filter = "componentName eq 'DeviceCompliancePolicy'"
        audit_data = makeAuditRequest(graph_filter, token)

    for policy in data["value"]:
        if prefix and not check_prefix_match(policy["name"], prefix):
            continue

        # Is the policy a Linux discovery script?
        if _check_linux_discovery_script(policy):
            # Get the detection script ID
            detection_script_id_path = _get_detection_script_id(policy)
            if detection_script_id_path is not None:
                detection_script_id = _get_value_from_path(
                    policy, detection_script_id_path
                )
                # get the script name
                detection_script = makeapirequest(
                    "https://graph.microsoft.com/beta/deviceManagement/reusablePolicySettings/",
                    token,
                    {"$filter": f"id eq '{detection_script_id}'"},
                )
                if detection_script["value"]:
                    policy["detectionScriptName"] = detection_script["value"][0][
                        "displayName"
                    ]

        # get scheduledActionsForRule
        scheduledActionsForRule = makeapirequest(
            f"{ENDPOINT}/{policy['id']}/scheduledActionsForRule",
            token,
            {"$expand": "scheduledActionConfigurations"},
        )

        policy["scheduledActionsForRule"] = scheduledActionsForRule["value"]

        results["config_count"] += 1
        print("Backing up compliance policy: " + policy["name"])

        if scope_tags:
            policy = get_scope_tags_name(policy, scope_tags)

        if "assignments" not in exclude:
            assignments = get_object_assignment(policy["id"], assignment_responses)
            if assignments:
                policy["assignments"] = assignments

        graph_id = policy["id"]
        policy = remove_keys(policy)
        for rule in policy["scheduledActionsForRule"]:
            remove_keys(rule)
        if policy["scheduledActionsForRule"]:
            for scheduled_config in policy["scheduledActionsForRule"][0][
                "scheduledActionConfigurations"
            ]:
                remove_keys(scheduled_config)

        # Get filename without illegal characters
        fname = clean_filename(policy["name"])
        if append_id:
            fname = f"{fname}_{policy['technologies']}__{graph_id}"
        else:
            fname = f"{fname}_{policy['technologies']}"
        # Save Compliance policy as JSON or YAML depending on configured value
        # in "-o"
        save_output(
            output,
            configpath,
            fname,
            policy,
        )

        results["outputs"].append(fname)

        if audit_data:
            compare_data = {"type": "resourceId", "value": graph_id}
            process_audit_data(
                audit_data, compare_data, path, f"{configpath}{fname}.{output}"
            )

    return results
