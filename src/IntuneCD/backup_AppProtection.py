#!/usr/bin/env python3

"""
This module backs up all App Protection Polices in Intune.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .graph_batch import batch_assignment, get_object_assignment
from .save_output import save_output
from .remove_keys import remove_keys
from .check_prefix import check_prefix_match

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/managedAppPolicies"


# Get all App Protection policies and save them in specified path
def savebackup(path, output, exclude, token, prefix):
    """
    Saves all App Protection policies in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: List of policies to exclude from the backup
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    configpath = path + "/" + "App Protection/"
    data = makeapirequest(ENDPOINT, token)

    assignment_responses = batch_assignment(
        data, "deviceAppManagement/", "/assignments", token, app_protection=True
    )

    # If profile is ManagedAppConfiguration, skip to next
    for profile in data["value"]:
        if prefix and not check_prefix_match(profile["displayName"], prefix):
            continue

        if profile["@odata.type"] == "#microsoft.graph.targetedManagedAppConfiguration":
            continue

        results["config_count"] += 1

        if "assignments" not in exclude:
            assignments = get_object_assignment(profile["id"], assignment_responses)
            if assignments:
                profile["assignments"] = assignments

        profile = remove_keys(profile)

        print("Backing up App Protection: " + profile["displayName"])

        if "targetedAppManagementLevels" in profile:
            fname = clean_filename(
                f"{profile['displayName']}_{profile['targetedAppManagementLevels']}"
            )
        else:
            fname = clean_filename(
                f"{profile['displayName']}_{str(profile['@odata.type'].split('.')[2])}"
            )

        # Save App Protection as JSON or YAML depending on configured value in
        # "-o"
        save_output(output, configpath, fname, profile)

        results["outputs"].append(fname)

    return results
