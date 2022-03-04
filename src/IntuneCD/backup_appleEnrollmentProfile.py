#!/usr/bin/env python3

"""
This module backs up all Apple Enrollment Profiles in Intune.

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
from .graph_batch import batch_request

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/depOnboardingSettings/"

## Get all Apple Enrollment Profiles and save them in specified path
def savebackup(path, output, token):
    configpath = path+"/"+"Enrollment Profiles/Apple/"
    data = makeapirequest(endpoint, token)

    profile_ids = []
    for profile in data['value']:
        profile_ids.append(profile['id'])

    batch_profile_data = batch_request(profile_ids,'deviceManagement/depOnboardingSettings/','/enrollmentProfiles',token)

    for profile in batch_profile_data:
        for value in profile['value']:
            remove_keys = {'id', 'createdDateTime', 'version',
                        'lastModifiedDateTime', 'isDefault'}
            for k in remove_keys:
                value.pop(k, None)

            print("Backing up Apple enrollment profile: " + value['displayName'])
            if os.path.exists(configpath) == False:
                os.makedirs(configpath)

            ## Get filename without illegal characters
            fname = clean_filename(value['displayName'])
            ## Save Apple Enrollment Pofile as JSON or YAML depending on configured value in "-o"
            if output != "json":
                with open(configpath+fname+".yaml", 'w') as yamlFile:
                    yaml.dump(value, yamlFile, sort_keys=False,
                            default_flow_style=False)
            else:
                with open(configpath+fname+".json", 'w') as jsonFile:
                    json.dump(value, jsonFile, indent=10)