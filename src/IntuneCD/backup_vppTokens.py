#!/usr/bin/env python3

"""
This module backs up all VPP tokens in Intune.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .save_output import save_output
from .remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/vppTokens"


# Get all VPP tokens and save them in specified path
def savebackup(path, output, token):
    """
    Save all VPP tokens in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    config_count = 0
    configpath = f'{path}/Apple VPP Tokens/'
    data = makeapirequest(ENDPOINT, token)

    for vpp_token in data['value']:
        config_count += 1
        token_name = vpp_token['displayName']
        vpp_token = remove_keys(vpp_token)

        print(f'Backing up VPP token: {token_name}')

        # Get filename without illegal characters
        fname = clean_filename(token_name)

        # Save token as JSON or YAML depending on configured value in "-o"
        save_output(output, configpath, fname, vpp_token)

    return config_count
