#!/usr/bin/env python3

"""
This module backs up all Windows Enrollment Profiles in Intune.

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
from .graph_batch import batch_assignment,get_object_assignment

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/windowsAutopilotDeploymentProfiles"

## Get all Windows Enrollment Profiles and save them in specified path
def savebackup(path, output, exclude, token):
    configpath = path+"/"+"Enrollment Profiles/Windows/"
    data = makeapirequest(endpoint, token)

    assignment_responses = batch_assignment(data,'deviceManagement/windowsAutopilotDeploymentProfiles/','/assignments',token)

    for profile in data['value']:
        if "assignments" not in exclude:
            assignments = get_object_assignment(profile['id'],assignment_responses)
            if assignments:
                profile['assignments'] = assignments
        
        remove_keys = {'id', 'createdDateTime',
                       'version', 'lastModifiedDateTime'}
        for k in remove_keys:
            profile.pop(k, None)
        print("Backing up Autopilot enrollment profile: " +
              profile['displayName'])
        if os.path.exists(configpath) == False:
            os.makedirs(configpath)

        ## Get filename without illegal characters
        fname = clean_filename(profile['displayName'])
        ## Save Windows Enrollment Profile as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+fname+".yaml", 'w') as yamlFile:
                yaml.dump(profile, yamlFile, sort_keys=False,
                          default_flow_style=False)
        else:
            with open(configpath+fname+".json", 'w') as jsonFile:
                json.dump(profile, jsonFile, indent=10)