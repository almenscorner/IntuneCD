#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Windows Feature Update Profiles in Intune.
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
ENDPOINT = (
    "https://graph.microsoft.com/beta/deviceManagement/windowsFeatureUpdateProfiles"
)


# Get all Windows Feature Profiles and save them in specified path
def savebackup(path, output, exclude, token, prefix, append_id, audit, scope_tags):
    """
    Saves all Windows Feature Update Profiles in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    audit_data = None
    configpath = path + "/" + "Feature Updates/"
    data = makeapirequest(ENDPOINT, token)

    assignment_responses = batch_assignment(
        data,
        "deviceManagement/windowsFeatureUpdateProfiles/",
        "/assignments",
        token,
    )
    if audit:
        graph_filter = "componentName eq 'SoftwareUpdateConfiguration'"
        audit_data = makeAuditRequest(graph_filter, token)

    for profile in data["value"]:
        if prefix and not check_prefix_match(profile["displayName"], prefix):
            continue

        results["config_count"] += 1

        if scope_tags:
            profile = get_scope_tags_name(profile, scope_tags)
        if "assignments" not in exclude:
            assignments = get_object_assignment(profile["id"], assignment_responses)
            if assignments:
                profile["assignments"] = assignments

        graph_id = profile["id"]
        profile = remove_keys(profile)

        print("Backing up Feature Update profile: " + profile["displayName"])

        # Get filename without illegal characters
        fname = clean_filename(profile["displayName"])
        if append_id:
            fname = f"{fname}__{graph_id}"
        # Save Windows Enrollment Profile as JSON or YAML depending on
        # configured value in "-o"
        save_output(output, configpath, fname, profile)

        results["outputs"].append(fname)

        if audit_data:
            compare_data = {"type": "resourceId", "value": graph_id}
            process_audit_data(
                audit_data, compare_data, path, f"{configpath}{fname}.{output}"
            )

    return results
