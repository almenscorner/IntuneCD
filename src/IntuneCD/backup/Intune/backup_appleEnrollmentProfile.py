#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Apple Enrollment Profiles in Intune.
"""

from ...intunecdlib.check_prefix import check_prefix_match
from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import batch_request
from ...intunecdlib.graph_request import makeapirequest, makeAuditRequest
from ...intunecdlib.process_audit_data import process_audit_data
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/depOnboardingSettings/"


# Get all Apple Enrollment Profiles and save them in specified path
def savebackup(path, output, token, prefix, append_id, audit):
    """
    Saves all Apple Enrollment Profiles in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    audit_data = None
    configpath = path + "/" + "Enrollment Profiles/Apple/"
    data = makeapirequest(ENDPOINT, token)
    if audit:
        graph_filter = "componentName eq 'Enrollment'"
        audit_data = makeAuditRequest(graph_filter, token)

    if data["value"]:
        profile_ids = []
        for profile in data["value"]:
            profile_ids.append(profile["id"])

        batch_profile_data = batch_request(
            profile_ids,
            "deviceManagement/depOnboardingSettings/",
            "/enrollmentProfiles",
            token,
        )

        for profile in batch_profile_data:
            results["config_count"] += 1
            for value in profile["value"]:
                if prefix and not check_prefix_match(value["displayName"], prefix):
                    continue

                graph_id = value["id"]
                value = remove_keys(value)

                print("Backing up Apple enrollment profile: " + value["displayName"])

                # Get filename without illegal characters
                fname = clean_filename(value["displayName"])
                if append_id:
                    fname = f"{fname}__{graph_id}"
                # Save Apple Enrollment Profile as JSON or YAML depending on
                # configured value in "-o"
                save_output(output, configpath, fname, value)

                results["outputs"].append(fname)

                if audit_data:
                    compare_data = {"type": "resourceId", "value": graph_id}
                    process_audit_data(
                        audit_data, compare_data, path, f"{configpath}{fname}.{output}"
                    )

    return results
