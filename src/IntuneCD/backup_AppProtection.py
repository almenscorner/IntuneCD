#!/usr/bin/env python3

"""
This module backs up all App Protection Polices in Intune.

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
endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/managedAppPolicies"

## Get all App Protection policies and save them in specified path
def savebackup(path,output,token):
    configpath = path+"/"+"App Protection/"
    data = makeapirequest(endpoint,token)

    for profile in data['value']:
        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime'}
        for k in remove_keys:
            profile.pop(k, None)
        print("Backing up App Protection: " + profile['displayName'])
        if os.path.exists(configpath)==False:
            os.mkdir(configpath)

        ## Save App Protection as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+profile['displayName']+".yaml",'w') as yamlFile:
                yaml.dump(profile, yamlFile, sort_keys=False, default_flow_style=False)
        else:
            with open(configpath+profile['displayName']+".json",'w') as jsonFile:
                json.dump(profile, jsonFile, indent=10)