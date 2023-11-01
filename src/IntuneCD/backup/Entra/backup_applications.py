#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up Applications in Entra.
"""

from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_request import makeapirequest
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/v1.0/myorganization/applications"


# Get Applications information and save in specified path
def savebackup(path, output, token):
    """
    Save Applications to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}

    configpath = path + "/" + "Entra/Applications/"
    data = makeapirequest(ENDPOINT, token)

    if data:
        for app in data["value"]:
            results["config_count"] += 1
            data = remove_keys(app)
            print(f'Backing up Entra Application {app["displayName"]}')

            # Get filename without illegal characters
            fname = clean_filename(app["displayName"])
            # Save APNs as JSON or YAML depending on configured value in "-o"
            save_output(output, configpath, fname, data)

            results["outputs"].append(fname)

    return results
