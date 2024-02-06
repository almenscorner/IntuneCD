#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Roles in Intune.
"""

from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_request import makeapirequest
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/roleDefinitions"


# Get all Roles and save them in specified path
def savebackup(path, output, exclude, token, append_id):
    """
    Saves all Roles in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    configpath = path + "/" + "Roles/"
    data = makeapirequest(ENDPOINT, token)

    for role in data["value"]:
        results["config_count"] += 1
        print("Backing up Role: " + role["displayName"])

        if "assignments" not in exclude:
            assignments = makeapirequest(
                ENDPOINT + f"/{role['id']}/roleAssignments", token
            )

            if assignments["value"]:
                role["roleAssignments"] = []
                for assignment in assignments["value"]:
                    role_assignment = makeapirequest(
                        f"https://graph.microsoft.com/beta/deviceManagement/roleAssignments/{assignment['id']}",
                        token,
                    )

                role["roleAssignments"].append(role_assignment)

        graph_id = role["id"]
        role = remove_keys(role)

        # Get filename without illegal characters
        fname = clean_filename(role["displayName"])
        if append_id:
            fname = f"{fname}__{graph_id}"
        # Save Compliance policy as JSON or YAML depending on configured
        # value in "-o"
        save_output(output, configpath, fname, role)

        results["outputs"].append(fname)

    return results
