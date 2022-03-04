#!/usr/bin/env python3

"""
This module backs up Managed Google Play setting in Intune.

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
endpoint = "https://graph.microsoft.com/beta/deviceManagement/androidManagedStoreAccountEnterpriseSettings"

## Get Managed Google Play information and save in specified path
def savebackup(path, output, token):
    configpath = f'{path}/Managed Google Play/'
    data = makeapirequest(endpoint, token)

    if data:
        remove_keys = {'id', 'companyCodes'}
        for k in remove_keys:
            data.pop(k, None)
        print("Backing up Managed Google Play: " +
              data['ownerUserPrincipalName'])
        if os.path.exists(configpath) == False:
            os.mkdir(configpath)

        ## Get filename without illegal characters
        fname = clean_filename(data['ownerUserPrincipalName'])
        ## Save Managed Google Play as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(f'{configpath}{fname}.yaml', 'w') as yamlFile:
                yaml.dump(data, yamlFile, sort_keys=False,
                          default_flow_style=False)
        else:
            with open(f'{configpath}{fname}.json', 'w') as jsonFile:
                json.dump(data, jsonFile, indent=10)