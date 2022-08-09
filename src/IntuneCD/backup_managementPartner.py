#!/usr/bin/env python3

"""
This module backs up all Management Partners in Intune.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .save_output import save_output
from .remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceManagementPartners"


# Get all Management Partners and save them in specified path
def savebackup(path, output, token):
    """
    Saves Management Partner information in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    config_count = 0
    configpath = path + "/" + "Partner Connections/Management/"
    data = makeapirequest(ENDPOINT, token)

    for partner in data['value']:
        if partner['isConfigured'] is False:
            continue

        config_count += 1
        print("Backing up Management Partner: " + partner['displayName'])

        partner = remove_keys(partner)

        # Get filename without illegal characters
        fname = clean_filename(partner['displayName'])
        # Save Compliance policy as JSON or YAML depending on configured
        # value in "-o"
        save_output(output, configpath, fname, partner)

    return config_count
