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
from .graph_request import makeapirequest

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/depOnboardingSettings/"

## Get all Apple Enrollment Profiles and save them in specified path
def savebackup(path,output,token):
    configpath = path+"/"+"Enrollment Profiles/Apple/"
    data = makeapirequest(endpoint,token)

    for profile in data['value']:
        profile_data = makeapirequest(endpoint + profile['id'] + '/enrollmentProfiles',token)
        for p in profile_data['value']:
            p_data = makeapirequest(endpoint + profile['id'] + '/enrollmentProfiles/' + p['id'],token)
            remove_keys = {'id','createdDateTime','version','lastModifiedDateTime','isDefault'}
            for k in remove_keys:
                p_data.pop(k, None)

            print("Backing up Apple enrollment profile: " + p['displayName'])
            if os.path.exists(configpath)==False:
                os.makedirs(configpath)

            ## Save Apple Enrollment Pofile as JSON or YAML depending on configured value in "-o"
            if output != "json":
                with open(configpath+p_data['displayName']+".yaml",'w') as yamlFile:
                    yaml.dump(p_data, yamlFile, sort_keys=False, default_flow_style=False)
            else:
                with open(configpath+p_data['displayName']+".json",'w') as jsonFile:
                    json.dump(p_data, jsonFile, indent=10)