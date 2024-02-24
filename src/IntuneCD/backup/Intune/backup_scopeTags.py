#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up Scope Tags in Intune.
"""

from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import batch_assignment, get_object_assignment
from ...intunecdlib.graph_request import makeapirequest, makeAuditRequest
from ...intunecdlib.process_audit_data import process_audit_data
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/roleScopeTags"


# Get Scope Tags and save in specified path
def savebackup(path, output, exclude, token, append_id, audit):
    """
    Save Scope Tags to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}

    configpath = path + "/" + "Scope Tags/"
    data = makeapirequest(ENDPOINT, token)

    assignment_responses = batch_assignment(
        data, "deviceManagement/roleScopeTags/", "/assignments", token
    )

    for tag in data["value"]:
        results["config_count"] += 1
        print("Backing up Scope Tag: " + tag["displayName"])

        tag_id = tag["id"]
        remove_keys(tag)

        if "assignments" not in exclude:
            assignments = get_object_assignment(tag_id, assignment_responses)
            if assignments:
                tag["assignments"] = assignments

        # Get filename without illegal characters
        fname = clean_filename(tag["displayName"])

        if append_id:
            fname = f"{fname}__{tag_id}"
        # Save Scope Tag as JSON or YAML depending on configured value in "-o"
        save_output(output, configpath, fname, tag)

        results["outputs"].append(fname)

        if audit:
            audit_data = makeAuditRequest(
                tag_id,
                "",
                token,
            )
            if audit_data:
                process_audit_data(audit_data, path, f"{configpath}{fname}.{output}")

    return results
