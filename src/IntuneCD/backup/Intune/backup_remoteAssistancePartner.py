#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Remote Assistance Partners in Intune.
"""

from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_request import makeapirequest, makeAuditRequest
from ...intunecdlib.process_audit_data import process_audit_data
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/remoteAssistancePartners"


# Get all Remote Assistance Partners and save them in specified path
def savebackup(path, output, token, append_id, audit):
    """
    Saves all Remote Assistance Partners in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    audit_data = None
    configpath = path + "/" + "Partner Connections/Remote Assistance/"
    data = makeapirequest(ENDPOINT, token)
    if audit:
        graph_filter = "componentName eq 'ManagedDevices'"
        audit_data = makeAuditRequest(graph_filter, token)

    for partner in data["value"]:
        if partner["onboardingStatus"] == "notOnboarded":
            continue

        results["config_count"] += 1
        print("Backing up Remote Assistance Partner: " + partner["displayName"])

        graph_id = partner["id"]
        partner = remove_keys(partner)

        # Get filename without illegal characters
        fname = clean_filename(partner["displayName"])
        if append_id:
            fname = f"{fname}__{graph_id}"
        # Save Compliance policy as JSON or YAML depending on configured
        # value in "-o"
        save_output(output, configpath, fname, partner)

        results["outputs"].append(fname)

        if audit_data:
            compare_data = {"type": "resourceId", "value": graph_id}
            process_audit_data(
                audit_data, compare_data, path, f"{configpath}{fname}.{output}"
            )

    return results
