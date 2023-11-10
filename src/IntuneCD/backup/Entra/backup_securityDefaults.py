#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up Security Defaults in Entra.
"""

from ...intunecdlib.graph_request import makeapirequest
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/v1.0/policies/identitySecurityDefaultsEnforcementPolicy"


# Get Security Defaults information and save in specified path
def savebackup(path, output, token):
    """
    Save Security Defaults to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}

    configpath = path + "/" + "Entra/Security Defaults/"
    data = makeapirequest(ENDPOINT, token)

    if data:
        results["config_count"] += 1
        data = remove_keys(data)
        print("Backing up Entra Security Defaults")

        # Get filename without illegal characters
        fname = "security_defaults"
        # Save APNs as JSON or YAML depending on configured value in "-o"
        save_output(output, configpath, fname, data)

        results["outputs"].append(fname)

    return results
