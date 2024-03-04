#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Configuration Policies in Intune.
"""

from ...intunecdlib.check_prefix import check_prefix_match
from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import (
    batch_assignment,
    batch_request,
    get_object_assignment,
    get_object_details,
)
from ...intunecdlib.graph_request import makeapirequest, makeAuditRequest
from ...intunecdlib.process_audit_data import process_audit_data
from ...intunecdlib.process_scope_tags import get_scope_tags_name
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph base endpoint
BASE_ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement"


# Get all Configuration Policies and save them in specified path
def savebackup(path, output, exclude, token, prefix, append_id, audit, scope_tags):
    """
    Saves all Configuration Policies in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    audit_data = None
    configpath = path + "/" + "Settings Catalog/"
    policies = makeapirequest(BASE_ENDPOINT + "/configurationPolicies", token)
    policy_ids = []
    for policy in policies["value"]:
        policy_ids.append(policy["id"])

    assignment_responses = batch_assignment(
        policies, "deviceManagement/configurationPolicies/", "/assignments", token
    )
    policy_settings_batch = batch_request(
        policy_ids,
        "deviceManagement/configurationPolicies/",
        "/settings?&top=1000",
        token,
    )
    if audit:
        graph_filter = "componentName eq 'DeviceConfiguration'"
        audit_data = makeAuditRequest(graph_filter, token)

    for policy in policies["value"]:
        if prefix and not check_prefix_match(policy["name"], prefix):
            continue

        results["config_count"] += 1
        name = policy["name"]
        print("Backing up configuration policy: " + name)

        settings = get_object_details(policy["id"], policy_settings_batch)

        if settings:
            policy["settings"] = settings

        if scope_tags:
            policy = get_scope_tags_name(policy, scope_tags)

        if "assignments" not in exclude:
            assignments = get_object_assignment(policy["id"], assignment_responses)
            if assignments:
                policy["assignments"] = assignments

        graph_id = policy["id"]
        policy = remove_keys(policy)

        # Get filename without illegal characters
        # fname = clean_filename(name)
        fname = clean_filename(
            f"{name}_{str(policy['technologies']).rsplit(',', 1)[-1]}"
        )
        if append_id:
            fname = f"{fname}__{graph_id}"
        # Save Configuration Policy as JSON or YAML depending on configured
        # value in "-o"
        save_output(output, configpath, fname, policy)

        results["outputs"].append(fname)

        if audit_data:
            compare_data = {"type": "resourceId", "value": graph_id}
            process_audit_data(
                audit_data, compare_data, path, f"{configpath}{fname}.{output}"
            )

    return results
