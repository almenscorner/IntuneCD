#!/usr/bin/env python3

"""
This module backs up all Configuration Policies in Intune.

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

## Set MS Graph base endpoint
baseEndpoint = "https://graph.microsoft.com/beta/deviceManagement"

## Get all Configuration Policies and save them in specified path
def savebackup(path,output,token):
    configpath = path+"/"+"Settings Catalog/"
    policies = makeapirequest(baseEndpoint + "/configurationPolicies",token)

    for policy in policies['value']:
        name = policy['name']
        print("Backing up configuration policy: " + name)
        if os.path.exists(configpath)==False:
            os.mkdir(configpath)
        
        ## Get all settings for the policy and add them to the dict
        policy_settings = makeapirequest(baseEndpoint + "/configurationPolicies" + "/" + policy['id'] + "/settings",token)
        policy['settings'] = policy_settings['value']

        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime'}
        for k in remove_keys:
            policy.pop(k, None)

        ## Save Configuration Policy as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+name+".yaml",'w') as yamlFile:
                yaml.dump(policy, yamlFile, sort_keys=False, default_flow_style=False)
        else:
            with open(configpath+name+".json",'w') as jsonFile:
                json.dump(policy, jsonFile, indent=10)