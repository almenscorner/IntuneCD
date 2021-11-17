#!/usr/bin/env python3

"""
This module backs up all Notification Templates in Intune.

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
endpoint = "https://graph.microsoft.com/beta/deviceManagement/notificationMessageTemplates"

## Get all Notification Templates and save them in specified path
def savebackup(path,output,token):
    configpath = path+"/"+"Compliance Policies/Message Templates/"
    q_param = "?$expand=localizedNotificationMessages"
    data = makeapirequest(endpoint,token,q_param)

    for template in data['value']:
        print("Backing up Notification message template: " + template['displayName'])
        q_param = "?$expand=localizedNotificationMessages"
        template_data = makeapirequest(endpoint + "/" + template['id'],token,q_param)

        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime'}
        for k in remove_keys:
            template_data.pop(k, None)

        if os.path.exists(configpath)==False:
            os.makedirs(configpath)

        ## Save App Condiguration as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+template_data['displayName']+".yaml",'w') as yamlFile:
                yaml.dump(template_data, yamlFile, sort_keys=False, default_flow_style=False)
        else:
            with open(configpath+template_data['displayName']+".json",'w') as jsonFile:
                json.dump(template_data, jsonFile, indent=10)