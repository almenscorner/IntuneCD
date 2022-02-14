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

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .get_add_assignments import get_assignments
from .match_wildcard import isMatching

## Set MS Graph endpoint
q_param = {"$filter":"(microsoft.graph.managedApp/appAvailability) eq null or (microsoft.graph.managedApp/appAvailability) eq 'lineOfBusiness' or isAssigned eq true"}
endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"

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
        if isMatching(str(app['@odata.type']).lower(),'*ios*') is True:
            platform = 'iOS'
        if isMatching(str(app['@odata.type']).lower(),'*macos*') is True:
            platform = 'macOS'
        if isMatching(str(app['@odata.type']).lower(),'*android*') is True:
            platform = 'Android'
        if isMatching(str(app['@odata.type']).lower(),'*windows*') is True:
            platform = 'Windows'

        print(f'Backing up Application: {app_name}')
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