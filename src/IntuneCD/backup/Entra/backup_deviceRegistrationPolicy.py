#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up Device Registration settings in Entra.
"""

from ...intunecdlib.graph_request import makeapirequest
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/policies/deviceRegistrationPolicy"


# Get Device Registration information and save in specified path
def savebackup(path, output, token):
    """
    Save Device Registration Policy settings to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}

    configpath = path + "/" + "Entra/Device Registration Policy/"
    data = makeapirequest(ENDPOINT, token)

    if data:
        results["config_count"] += 1
        data = remove_keys(data)
        print("Backing up Entra Device Registration Policy")

        # Get filename without illegal characters
        fname = "device_registration_policy"
        # Save APNs as JSON or YAML depending on configured value in "-o"
        save_output(output, configpath, fname, data)

        results["outputs"].append(fname)

    return results
