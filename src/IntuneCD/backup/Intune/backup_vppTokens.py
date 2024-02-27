#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all VPP tokens in Intune.
"""

from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_request import makeapirequest, makeAuditRequest
from ...intunecdlib.process_audit_data import process_audit_data
from ...intunecdlib.process_scope_tags import get_scope_tags_name
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/vppTokens"


# Get all VPP tokens and save them in specified path
def savebackup(path, output, token, append_id, audit, scope_tags):
    """
    Save all VPP tokens in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    audit_data = None
    configpath = f"{path}/Apple VPP Tokens/"
    data = makeapirequest(ENDPOINT, token)
    if audit:
        graph_filter = "componentName eq 'MobileApp'"
        audit_data = makeAuditRequest(graph_filter, token)

    for vpp_token in data["value"]:
        results["config_count"] += 1
        token_name = vpp_token["displayName"]
        graph_id = vpp_token["id"]
        vpp_token = remove_keys(vpp_token)

        print(f"Backing up VPP token: {token_name}")

        if scope_tags:
            vpp_token = get_scope_tags_name(vpp_token, scope_tags)

        # Get filename without illegal characters
        fname = clean_filename(token_name)
        if append_id:
            fname = f"{fname}__{graph_id}"

        # Save token as JSON or YAML depending on configured value in "-o"
        save_output(output, configpath, fname, vpp_token)

        results["outputs"].append(fname)

        if audit_data:
            compare_data = {"type": "resourceId", "value": graph_id}
            process_audit_data(
                audit_data, compare_data, path, f"{configpath}{fname}.{output}"
            )

    return results
