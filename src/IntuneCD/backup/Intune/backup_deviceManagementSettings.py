#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up Device Management settings in Intune.
"""

from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_request import makeapirequest, makeAuditRequest
from ...intunecdlib.process_audit_data import process_audit_data
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/settings"


# Get settings and save in specified path
def savebackup(path, output, audit, token):
    """
    Save Device Management Setting to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    audit_data = None
    configpath = path + "/" + "Device Management Settings/"
    data = makeapirequest(ENDPOINT, token)
    if audit:
        graph_filter = (
            "resources/any(s:s/auditResourceType eq 'DeviceManagementSettings')"
        )
        audit_data = makeAuditRequest(graph_filter, token)

    if data:
        results["config_count"] += 1
        data = remove_keys(data)
        print("Backing up Device Management Settings")

        # Get filename without illegal characters
        fname = clean_filename("settings")
        # Save settings as JSON or YAML depending on configured value in "-o"
        save_output(output, configpath, fname, data)

        results["outputs"].append(fname)

        if audit_data:
            compare_data = {
                "type": "auditResourceType",
                "value": "DeviceManagementSettings",
            }
            process_audit_data(
                audit_data, compare_data, path, f"{configpath}{fname}.{output}"
            )

    return results
