#!/usr/bin/env python3

"""
This module backs up all App Protection Polices in Intune.

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
endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/managedAppPolicies"

## Get all App Protection policies and save them in specified path
def savebackup(path,output,token):
    configpath = path+"/"+"App Protection/"
    data = makeapirequest(endpoint,token)

    ## If profile is ManagedAppConfiguration, skip to next
    for profile in data['value']:
        if profile['@odata.type'] == "#microsoft.graph.targetedManagedAppConfiguration":
            continue
        
        pid = profile['id']
        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime','deployedAppCount','isAssigned'}
        for k in remove_keys:
            profile.pop(k, None)
        print("Backing up App Protection: " + profile['displayName'])
        if os.path.exists(configpath)==False:
            os.mkdir(configpath)

        if profile['@odata.type'] == "#microsoft.graph.iosManagedAppProtection":
            platform = "ios"
        elif profile['@odata.type'] == "#microsoft.graph.androidManagedAppProtection":
            platform = "android"
        elif profile['@odata.type'] == "#microsoft.graph.windowsManagedAppProtection":
            platform = "windows"
        elif profile['@odata.type'] == "#microsoft.graph.mdmWindowsInformationProtectionPolicy":
            platform = "mdmWindowsInformationProtectionPolicies"
        elif profile['@odata.type'] == "#microsoft.graph.targetedManagedAppConfiguration":
            platform = None

        if platform == "mdmWindowsInformationProtectionPolicies":
            platform_endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/" + platform
        else: 
            platform_endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/" + platform + "ManagedAppProtections"
            
        get_assignments(platform_endpoint,profile,pid,token)

        ## Get filename without illegal characters
        fname = clean_filename(profile['displayName'])
        ## Save App Protection as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+fname+".yaml",'w') as yamlFile:
                yaml.dump(profile, yamlFile, sort_keys=False, default_flow_style=False)
        else:
            with open(configpath+fname+".json",'w') as jsonFile:
                json.dump(profile, jsonFile, indent=10)