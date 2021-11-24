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

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .get_add_assignments import get_assignments

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/deviceCompliancePolicies"

## Get all Compliance policies and save them in specified path
def savebackup(path,output,token):
    configpath = path+"/"+"Compliance Policies/Policies/"
    q_param = {"$expand":"scheduledActionsForRule($expand=scheduledActionConfigurations)"}
    data = makeapirequest(endpoint,token,q_param)

    for policy in data['value']:
        print("Backing up compliance policy: " + policy['displayName'])

        pid = policy['id']
        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime','@odata.context','scheduledActionConfigurations@odata.context','scheduledActionsForRule@odata.context'}
        for k in remove_keys:
            policy.pop(k, None)
            for rule in policy['scheduledActionsForRule']:
                rule.pop(k, None)
            if policy['scheduledActionsForRule']:
                for scheduled_config in policy['scheduledActionsForRule'][0]['scheduledActionConfigurations']:
                    scheduled_config.pop(k, None)

        if os.path.exists(configpath)==False:
            os.makedirs(configpath)

        ## Get assignments of Compliance Policy
        get_assignments(endpoint,policy,pid,token)

        ## Get filename without illegal characters
        fname = clean_filename(policy['displayName'])
        ## Save Compliance policy as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+fname+".yaml",'w') as yamlFile:
                yaml.dump(policy, yamlFile, sort_keys=False, default_flow_style=False)
        else:
            with open(configpath+fname+".json",'w') as jsonFile:
                json.dump(policy, jsonFile, indent=10)