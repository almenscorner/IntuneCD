#!/usr/bin/env python3

"""
This module backs up all VPP tokens in Intune.

Parameters
----------
path : str
    The path to save the backup to
output : str
    The format the backup will be saved as
token : str
    The token to use for authenticating the request
"""

import json
import os
import yaml

from .clean_filename import clean_filename
from .graph_request import makeapirequest

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/vppTokens"

## Get all VPP tokens and save them in specified path
def savebackup(path, output, token):
    configpath = f'{path}/Apple VPP Tokens/'
    data = makeapirequest(endpoint, token)

    for vpp_token in data['value']:
        token_name = vpp_token['displayName']
        remove_keys = {'id', 'createdDateTime', 'version',
                       'lastModifiedDateTime', 'token', 'lastSyncDateTime'}
        for k in remove_keys:
            vpp_token.pop(k, None)

        print(f'Backing up VPP token: {token_name}')

        if os.path.exists(configpath) == False:
            os.makedirs(configpath)

        ## Get filename without illegal characters
        fname = clean_filename(token_name)

        ## Save token as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(f'{configpath}{fname}.yaml', 'w') as yamlFile:
                yaml.dump(vpp_token, yamlFile, sort_keys=False,
                          default_flow_style=False)
        else:
            with open(f'{configpath}{fname}.json', 'w') as jsonFile:
                json.dump(vpp_token, jsonFile, indent=10)