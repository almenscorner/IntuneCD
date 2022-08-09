#!/usr/bin/env python3

"""
This module backs up Managed Google Play setting in Intune.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .save_output import save_output
from .remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/androidManagedStoreAccountEnterpriseSettings"


# Get Managed Google Play information and save in specified path
def savebackup(path, output, token):
    """
    Saves Managed Google Play information in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    config_count = 0
    configpath = f'{path}/Managed Google Play/'
    data = makeapirequest(ENDPOINT, token)

    if data:
        config_count += 1
        data = remove_keys(data)
        print("Backing up Managed Google Play: " +
              data['ownerUserPrincipalName'])

        # Get filename without illegal characters
        fname = clean_filename(data['ownerUserPrincipalName'])
        # Save Managed Google Play as JSON or YAML depending on configured
        # value in "-o"
        save_output(output, configpath, fname, data)

    return config_count
