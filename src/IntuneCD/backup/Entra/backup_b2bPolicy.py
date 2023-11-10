#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up Security Defaults in Entra.
"""

from ...intunecdlib.azure_request import make_azure_request
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "B2B/b2bPolicy"


# Get Security Defaults information and save in specified path
def savebackup(path, output, token):
    """
    Save Security Defaults to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}

    configpath = path + "/" + "Entra/External Collaboration Settings/"
    data = make_azure_request(token, ENDPOINT)

    if data:
        results["config_count"] += 1
        data = remove_keys(data)
        print("Backing up Entra External Collaboration Settings B2B Policy")

        # Get filename without illegal characters
        fname = "b2b_policy"
        # Save APNs as JSON or YAML depending on configured value in "-o"
        save_output(output, configpath, fname, data)

        results["outputs"].append(fname)

    return results
