#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up Group settings in Entra.
"""

from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_request import makeapirequest
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/v1.0/groupSettings"


# Get Group Settings information and save in specified path
def savebackup(path, output, token):
    """
    Save Group settings to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}

    configpath = path + "/" + "Entra/Group Settings/"
    data = makeapirequest(ENDPOINT, token)

    if data:
        for setting in data["value"]:
            results["config_count"] += 1
            data = remove_keys(setting)
            print(f"Backing up Entra Group Setting {setting['displayName']}")

            # Get filename without illegal characters
            fname = clean_filename(setting["displayName"])
            # Save APNs as JSON or YAML depending on configured value in "-o"
            save_output(output, configpath, fname, data)

            results["outputs"].append(fname)

    return results
