#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Windows Quality Update Profiles in Intune.
"""

from ...intunecdlib.check_prefix import check_prefix_match
from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import batch_assignment, get_object_assignment
from ...intunecdlib.graph_request import makeapirequest
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = (
    "https://graph.microsoft.com/beta/deviceManagement/windowsQualityUpdateProfiles"
)


# Get all Windows Quality Profiles and save them in specified path
def savebackup(path, output, exclude, token, prefix, append_id):
    """
    Saves all Windows Quality Update Profiles in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    configpath = path + "/" + "Quality Updates/"
    data = makeapirequest(ENDPOINT, token)

    assignment_responses = batch_assignment(
        data,
        "deviceManagement/windowsQualityUpdateProfiles/",
        "/assignments",
        token,
    )

    for profile in data["value"]:
        if prefix and not check_prefix_match(profile["displayName"], prefix):
            continue

        results["config_count"] += 1
        if "assignments" not in exclude:
            assignments = get_object_assignment(profile["id"], assignment_responses)
            if assignments:
                profile["assignments"] = assignments

        graph_id = profile["id"]
        profile = remove_keys(profile)

        print("Backing up Quality Update profile: " + profile["displayName"])

        # Get filename without illegal characters
        fname = clean_filename(profile["displayName"])
        if append_id:
            fname = f"{fname}__{graph_id}"
        # Save Windows Enrollment Profile as JSON or YAML depending on
        # configured value in "-o"
        save_output(output, configpath, fname, profile)

        results["outputs"].append(fname)

    return results
