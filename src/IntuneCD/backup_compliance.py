#!/usr/bin/env python3

"""
This module backs up all Compliance Polices in Intune.

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
endpoint = "https://graph.microsoft.com/beta/deviceManagement/deviceCompliancePolicies"

## Get all Compliance policies and save them in specified path
def savebackup(path,output,token):
    configpath = path+"/"+"Compliance Policies/Policies/"
    data = makeapirequest(endpoint,token)

    for policy in data['value']:
        print("Backing up compliance policy: " + policy['displayName'])
        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime'}
        for k in remove_keys:
            policy.pop(k, None)
        if os.path.exists(configpath)==False:
            os.makedirs(configpath)

        ## Save Compliance policy as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+policy['displayName']+".yaml",'w') as yamlFile:
                yaml.dump(policy, yamlFile, sort_keys=False, default_flow_style=False)
        else:
            with open(configpath+policy['displayName']+".json",'w') as jsonFile:
                json.dump(policy, jsonFile, indent=10)