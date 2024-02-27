#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Enrollment Configurations in Intune.
"""

import re

from ...intunecdlib.check_prefix import check_prefix_match
from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import batch_assignment, get_object_assignment
from ...intunecdlib.graph_request import makeapirequest, makeAuditRequest
from ...intunecdlib.process_audit_data import process_audit_data
from ...intunecdlib.process_scope_tags import get_scope_tags_name
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = (
    "https://graph.microsoft.com/beta/deviceManagement/deviceEnrollmentConfigurations"
)


# Get all Enrollment Configurations and save them in specified path
def savebackup(path, output, exclude, token, prefix, append_id, audit, scope_tags):
    """
    Saves all Enrollment Configurations in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    audit_data = None
    configpath = path + "/" + "Enrollment Configurations/"
    data = makeapirequest(ENDPOINT, token)

    assignment_responses = batch_assignment(
        data, "deviceManagement/deviceEnrollmentConfigurations/", "/assignments", token
    )
    if audit:
        graph_filter = "componentName eq 'Enrollment'"
        audit_data = makeAuditRequest(graph_filter, token)

    for config in data["value"]:
        if prefix and not check_prefix_match(config["displayName"], prefix):
            continue

        if (
            config["@odata.type"]
            == "#microsoft.graph.windows10EnrollmentCompletionPageConfiguration"
        ):
            continue
        results["config_count"] += 1
        config_type = config.get("deviceEnrollmentConfigurationType", None)
        config_type = config_type[0].upper() + config_type[1:]
        config_type = re.findall("[A-Z][^A-Z]*", config_type)
        config_type = " ".join(config_type)

        print(f"Backing up Enrollment Config {config_type}: " + config["displayName"])

        if scope_tags:
            config = get_scope_tags_name(config, scope_tags)

        if "assignments" not in exclude:
            assignments = get_object_assignment(config["id"], assignment_responses)
            if assignments:
                config["assignments"] = assignments

        graph_id = config["id"]
        fname = clean_filename(
            f"{config['displayName']}_{str(config['@odata.type']).split('.')[2]}"
        )
        if append_id:
            fname = f"{fname}__{graph_id}"

        config = remove_keys(config)

        # Get filename without illegal characters
        fname = clean_filename(fname)
        # Save Enrollment Configuration as JSON or YAML depending on configured
        # value in "-o"
        save_output(output, configpath, fname, config)

        results["outputs"].append(fname)

        if audit_data:
            compare_data = {"type": "resourceId", "value": graph_id}
            process_audit_data(
                audit_data, compare_data, path, f"{configpath}{fname}.{output}"
            )

    return results
