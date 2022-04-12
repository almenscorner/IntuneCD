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
from .graph_batch import batch_assignment, get_object_assignment

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/deviceCompliancePolicies"

## Get all Compliance policies and save them in specified path
def savebackup(path, output, exclude, token):
    configpath = path+"/"+"Compliance Policies/Policies/"
    q_param = {
        "$expand": "scheduledActionsForRule($expand=scheduledActionConfigurations)"}
    data = makeapirequest(endpoint, token, q_param)

    assignment_responses = batch_assignment(data,f'deviceManagement/deviceCompliancePolicies/','/assignments',token)

    for policy in data['value']:
        print("Backing up compliance policy: " + policy['displayName'])

        if "assignments" not in exclude:
            assignments = get_object_assignment(policy['id'],assignment_responses)
            if assignments:
                policy['assignments'] = assignments

        remove_keys = {'id', 'createdDateTime', 'version', 'lastModifiedDateTime', '@odata.context',
                       'scheduledActionConfigurations@odata.context', 'scheduledActionsForRule@odata.context'}
        for k in remove_keys:
            policy.pop(k, None)
            for rule in policy['scheduledActionsForRule']:
                rule.pop(k, None)
            if policy['scheduledActionsForRule']:
                for scheduled_config in policy['scheduledActionsForRule'][0]['scheduledActionConfigurations']:
                    scheduled_config.pop(k, None)

        if os.path.exists(configpath) == False:
            os.makedirs(configpath)

        ## Get filename without illegal characters
        fname = clean_filename(policy['displayName'])
        ## Save Compliance policy as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+fname+'_'+str(policy['@odata.type'].split('.')[2])+".yaml", 'w') as yamlFile:
                yaml.dump(policy, yamlFile, sort_keys=False,
                          default_flow_style=False)
        else:
            with open(configpath+fname+'_'+str(policy['@odata.type'].split('.')[2])+".json", 'w') as jsonFile:
                json.dump(policy, jsonFile, indent=10)