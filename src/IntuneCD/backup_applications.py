#!/usr/bin/env python3

"""
This module backs up all applications in Intune.

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
import re

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .get_add_assignments import get_assignments

## Set MS Graph endpoint
q_param = {"$filter":"(microsoft.graph.managedApp/appAvailability) eq null or (microsoft.graph.managedApp/appAvailability) eq 'lineOfBusiness' or isAssigned eq true"}
endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"

## Function to match platform from @odata.type
def match (platform,input) -> bool:
    string = f'.*{platform}.*$'
    pattern = re.compile(string)
    match =  pattern.match(input, re.IGNORECASE)
    if match:
        return True
    else:
        return False

## Get all applications and save them in specified path
def savebackup(path,output,token):
    configpath = f'{path}/Applications/'
    data = makeapirequest(endpoint,token,q_param)

    for app in data['value']:
        app_id = app['id']
        platform = ""
        remove_keys={'id','createdDateTime','version','lastModifiedDateTime','description'}
        for k in remove_keys:
            app.pop(k, None)
        
        ## If app type is VPP, add Apple ID to the name as the app can exist multiple times
        if app['@odata.type'] == '#microsoft.graph.iosVppApp':
            app_name = app['displayName']+'_iOSVppApp_'+str(app['vppTokenAppleId'].split('@')[0])
        elif app['@odata.type'] == '#microsoft.graph.macOsVppApp':
            app_name = app['displayName']+'_macOSVppApp_'+str(app['vppTokenAppleId'].split('@')[0])
        ## If app is not VPP, only add the app type to the name
        else:
            app_name = app['displayName']+'_'+str(app['@odata.type'].split('.')[2])

        ## Get application platform
        if match('ios',str(app['@odata.type']).lower()) is True:
            platform = 'iOS'
        if match('macos',str(app['@odata.type']).lower()) is True:
            platform = 'macOS'
        if match('android',str(app['@odata.type']).lower()) is True:
            platform = 'Android'
        if match('windows',str(app['@odata.type']).lower()) is True:
            platform = 'Windows'

        print(f"Backing up Application: {app['displayName']}")
        if os.path.exists(f'{configpath}/{platform}')==False:
            os.makedirs(f'{configpath}/{platform}')

        get_assignments(endpoint,app,app_id,token)
        ## Get filename without illegal characters
        fname = clean_filename(app_name)
        ## Save Applications as JSON or YAML depending on configured value in "-o"
        if output != 'json':
            with open(f'{configpath}{platform}/{fname}.yaml','w') as yamlFile:
                yaml.dump(app,yamlFile,sort_keys=False,default_flow_style=False)
        else:
            with open(f'{configpath}{platform}/{fname}.json','w') as jsonFile:
                json.dump(app,jsonFile,indent=10)