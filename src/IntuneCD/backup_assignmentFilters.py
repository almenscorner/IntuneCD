#!/usr/bin/env python3

"""
This module backs up all Filters in Intune.

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
from .graph_request import makeapirequest

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/assignmentFilters"

## Get all Filters and save them in specified path
def savebackup(path,output,token):
    configpath = path+"/"+"Filters/"
    data = makeapirequest(endpoint,token)

    for assign_filter in data['value']:
        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime','platform'}
        for k in remove_keys:
            assign_filter.pop(k, None)
        print("Backing up Filter: " + assign_filter['displayName'])
        if os.path.exists(configpath)==False:
            os.mkdir(configpath)

        ## Save Filters as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+assign_filter['displayName']+".yaml",'w') as yamlFile:
                yaml.dump(assign_filter, yamlFile, sort_keys=False, default_flow_style=False)
        else:
            with open(configpath+assign_filter['displayName']+".json",'w') as jsonFile:
                json.dump(assign_filter, jsonFile, indent=10)