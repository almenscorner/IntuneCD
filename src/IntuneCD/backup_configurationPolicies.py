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

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .get_add_assignments import get_assignments

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

        pid = policy['id']
        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime'}
        for k in remove_keys:
            policy.pop(k, None)

        ## Get assignments of Device Configuration
        get_assignments(baseEndpoint + "/configurationPolicies",policy,pid,token)

        ## Get filename without illegal characters
        fname = clean_filename(name)
        ## Save Configuration Policy as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+fname+".yaml",'w') as yamlFile:
                yaml.dump(policy, yamlFile, sort_keys=False, default_flow_style=False)
        else:
            with open(configpath+fname+".json",'w') as jsonFile:
                json.dump(policy, jsonFile, indent=10)