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
from .graph_batch import batch_assignment, get_object_assignment, batch_request, get_object_details

## Set MS Graph base endpoint
baseEndpoint = "https://graph.microsoft.com/beta/deviceManagement"

## Get all Configuration Policies and save them in specified path
def savebackup(path, output, exclude, token):
    configpath = path+"/"+"Settings Catalog/"
    policies = makeapirequest(baseEndpoint + "/configurationPolicies", token)
    policy_ids = []
    for policy in policies['value']:
        policy_ids.append(policy['id'])

    assignment_responses = batch_assignment(policies,f'deviceManagement/configurationPolicies/','/assignments',token)
    policy_settings_batch = batch_request(policy_ids,'deviceManagement/configurationPolicies/','/settings',token)

    for policy in policies['value']:
        name = policy['name']
        print("Backing up configuration policy: " + name)
        if os.path.exists(configpath) == False:
            os.mkdir(configpath)

        settings = get_object_details(policy['id'],policy_settings_batch)

        if settings:
            policy['settings'] = settings

        if "assignments" not in exclude:
            assignments = get_object_assignment(policy['id'],assignment_responses)
            if assignments:
                policy['assignments'] = assignments

        remove_keys = {'id', 'createdDateTime',
                       'version', 'lastModifiedDateTime'}
        for k in remove_keys:
            policy.pop(k, None)

        ## Get filename without illegal characters
        fname = clean_filename(name)
        ## Save Configuration Policy as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+fname+".yaml", 'w') as yamlFile:
                yaml.dump(policy, yamlFile, sort_keys=False,
                          default_flow_style=False)
        else:
            with open(configpath+fname+".json", 'w') as jsonFile:
                json.dump(policy, jsonFile, indent=10)