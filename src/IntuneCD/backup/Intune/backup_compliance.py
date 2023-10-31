#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Compliance Polices in Intune.
"""

from ...intunecdlib.check_prefix import check_prefix_match
from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import batch_assignment, get_object_assignment
from ...intunecdlib.graph_request import makeapirequest
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceCompliancePolicies"


# Get all Compliance policies and save them in specified path
def savebackup(path, output, exclude, token, prefix, append_id):
    """
    Saves all Compliance policies in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    configpath = path + "/" + "Compliance Policies/Policies/"
    q_param = {
        "$expand": "scheduledActionsForRule($expand=scheduledActionConfigurations)"
    }
    data = makeapirequest(ENDPOINT, token, q_param)

    assignment_responses = batch_assignment(
        data, "deviceManagement/deviceCompliancePolicies/", "/assignments", token
    )

    for policy in data["value"]:
        if prefix and not check_prefix_match(policy["displayName"], prefix):
            continue

        results["config_count"] += 1
        print("Backing up compliance policy: " + policy["displayName"])

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
        fname = clean_filename(policy["displayName"])
        if append_id:
            fname = f"{fname}_{policy['@odata.type'].split('.')[2]}__{graph_id}"
        else:
            fname = f"{fname}_{policy['@odata.type'].split('.')[2]}"
        # Save Compliance policy as JSON or YAML depending on configured value
        # in "-o"
        save_output(
            output,
            configpath,
            fname,
            policy,
        )

        results["outputs"].append(fname)

    return results
