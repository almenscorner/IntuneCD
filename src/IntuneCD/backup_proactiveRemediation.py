#!/usr/bin/env python3

"""
This module backs up all Proactive Remediations in Intune.

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
import base64
import yaml

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .graph_batch import batch_assignment, get_object_assignment, batch_request

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/deviceHealthScripts"

## Get all Proactive Remediations and save them in specified path
def savebackup(path, output, exclude, token):
    configpath = f'{path}/Proactive Remediations/'
    data = makeapirequest(endpoint, token)
    pr_ids = []
    for script in data['value']:
        pr_ids.append(script['id'])

    assignment_responses = batch_assignment(data,f'deviceManagement/deviceHealthScripts/','/assignments',token)
    pr_data_responses = batch_request(pr_ids,f'deviceManagement/deviceHealthScripts/','',token)

    for pr_details in pr_data_responses:
        if "Microsoft" not in pr_details['publisher']:
            
            if "assignments" not in exclude:
                assignments = get_object_assignment(pr_details['id'],assignment_responses)
                if assignments:
                    pr_details['assignments'] = assignments
                
            remove_keys = {'id', 'createdDateTime', 'version',
                           'lastModifiedDateTime', 'isGlobalScript', 'highestAvailableVersion'}
            for k in remove_keys:
                pr_details.pop(k, None)

            print(f"Backing up Proactive Remediation: {pr_details['displayName']}")
            if os.path.exists(configpath) == False:
                os.makedirs(configpath)

            ## Get filename without illegal characters
            fname = clean_filename(pr_details['displayName'])

            ## Save Proactive Remediation as JSON or YAML depending on configured value in "-o"
            if output != 'json':
                with open(f"{configpath}{fname}.yaml", 'w') as yamlFile:
                    yaml.dump(pr_details, yamlFile, sort_keys=False,
                              default_flow_style=False)
            else:
                with open(f"{configpath}{fname}.json", 'w') as jsonFile:
                    json.dump(pr_details, jsonFile, indent=10)

            if os.path.exists(f'{configpath}/Script Data') == False:
                os.makedirs(f'{configpath}/Script Data')

            ## Save detection script to the Script Data folder
            decoded = base64.b64decode(
                pr_details['detectionScriptContent']).decode('utf-8')
            f = open(
                f"{configpath}/Script Data/{pr_details['displayName']}_DetectionScript.ps1", 'w')
            f.write(decoded)
            ## Save remediation script to the Script Data folder
            decoded = base64.b64decode(
                pr_details['remediationScriptContent']).decode('utf-8')
            f = open(
                f"{configpath}/Script Data/{pr_details['displayName']}_RemediationScript.ps1", 'w')
            f.write(decoded)