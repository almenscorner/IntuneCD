#!/usr/bin/env python3

"""
This module backs up Device Categories in Intune.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .save_output import save_output
from .remove_keys import remove_keys
from .check_prefix import check_prefix_match

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceCategories"


# Get Device Categories information and save in specified path
def savebackup(path, output, token, prefix):
    """
    Save Device Categories to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}

    configpath = path + "/" + "Device Categories/"
    data = makeapirequest(ENDPOINT, token)

    if data["value"]:
        for item in data["value"]:
            if prefix and not check_prefix_match(item["displayName"], prefix):
                continue

            results["config_count"] += 1
            item = remove_keys(item)
            print("Backing up Device Category: " + item["displayName"])

            # Get filename without illegal characters
            fname = clean_filename(item["displayName"])
            # Save Device Categories as JSON or YAML depending on configured value in "-o"
            save_output(output, configpath, fname, item)

            results["outputs"].append(fname)

    return results
