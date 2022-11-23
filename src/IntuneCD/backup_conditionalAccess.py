#!/usr/bin/env python3

"""
This module backs up all Conditional Access in Intune.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .save_output import save_output
from .remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/identity/conditionalAccess/policies"


# Get all Conditional Access and save them in specified path
def savebackup(path, output, token):
    """
    Saves all Conditional Access in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    config_count = 0
    configpath = path + "/" + "Conditional Access/"
    data = makeapirequest(ENDPOINT, token)

    if data['value']:
        for policy in data['value']:
            config_count += 1
            print("Backing up Conditional Access policy: " + policy['displayName'])

            policy = makeapirequest(f"{ENDPOINT}/{policy['id']}", token)
            if policy['grantControls']:
                policy['grantControls'].pop('authenticationStrength@odata.context', None)
            policy = remove_keys(policy)

            # Get filename without illegal characters
            fname = clean_filename(policy['displayName'])
            # Save Conditional Access as JSON or YAML depending on configured
            # value in "-o"
            save_output(output, configpath, fname, policy)

        return config_count