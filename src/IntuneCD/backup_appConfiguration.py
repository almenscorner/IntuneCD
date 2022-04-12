#!/usr/bin/env python3

"""
This module backs up all App Configuration Polices in Intune.

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
endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/mobileAppConfigurations"
app_endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"

## Get all App Configuration policies and save them in specified path
def savebackup(path, output, exclude, token):
    configpath = path+"/"+"App Configuration/"
    data = makeapirequest(endpoint, token)

    assignment_responses = batch_assignment(data,f'deviceAppManagement/mobileAppConfigurations/','/assignments',token)

    for profile in data['value']:
        if "assignments" not in exclude:
            assignments = get_object_assignment(profile['id'],assignment_responses)
            if assignments:
                profile['assignments'] = assignments
            
        remove_keys = {'id', 'createdDateTime',
                       'version', 'lastModifiedDateTime'}
        for k in remove_keys:
            profile.pop(k, None)

        ## Get name and type of app on App Configuration Profile
        app_dict = {}
        for app_id in profile['targetedMobileApps']:
            app_data = makeapirequest(app_endpoint + "/" + app_id, token)
            if app_data:
                app_dict['appName'] = app_data['displayName']
                app_dict['type'] = app_data['@odata.type']

        if app_dict:
            profile.pop('targetedMobileApps')
            profile['targetedMobileApps'] = app_dict

        print("Backing up App Configuration: " + profile['displayName'])

        if os.path.exists(configpath) == False:
            os.mkdir(configpath)

        ## Get filename without illegal characters
        fname = clean_filename(f"{profile['displayName']}_{str(profile['@odata.type'].split('.')[2])}")
        ## Save App Condiguration as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+fname+".yaml", 'w') as yamlFile:
                yaml.dump(profile, yamlFile, sort_keys=False,
                          default_flow_style=False)
        else:
            with open(configpath+fname+".json", 'w') as jsonFile:
                json.dump(profile, jsonFile, indent=10)