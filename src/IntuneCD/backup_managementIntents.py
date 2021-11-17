#!/usr/bin/env python3

"""
This module backs up all Intents in Intune.

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

## Set MS Graph base endpoint
baseEndpoint = "https://graph.microsoft.com/beta/deviceManagement"

## Get all Intents and save them in specified path
def savebackup(path,output,token):
    configpath = path+"/"+"Management Intents/"
    intents = makeapirequest(baseEndpoint + "/intents",token)

    for intent in intents['value']:
        print("Backing up Intent: " + intent['displayName'])
        ## Get Intent template details
        intent_template = makeapirequest(baseEndpoint + "/templates" + "/" + intent['templateId'],token)
        ## Get Intent categories
        intent_template_categories = makeapirequest(baseEndpoint + "/templates" + "/" + intent['templateId'] + "/categories",token)

        configpath = path+"/"+"Management Intents/" + intent_template['displayName'] + "/"
        if os.path.exists(configpath)==False:
            os.makedirs(configpath)

        ## Save all setings for the Intent
        settings_delta = {}
        for intent_category in intent_template_categories['value']:
            intent_settings = makeapirequest(baseEndpoint + "/intents" + "/" + intent['id'] + "/categories" + "/" + intent_category['id'] + "/settings",token)
            settings_delta = intent_settings['value']

        intent_value = {
            "displayName": intent['displayName'],
            "description": intent['description'],
            "settingsDelta": settings_delta,
            "roleScopeTagIds": intent['roleScopeTagIds']
        }

        ## Save Intent as JSON or YAML depending on configured value in "-o"
        if output != "json":
            with open(configpath+intent['displayName']+".yaml",'w') as yamlFile:
                yaml.dump(intent_value, yamlFile, sort_keys=False, default_flow_style=False)
        else:
            with open(configpath+intent['displayName']+".json",'w') as jsonFile:
                json.dump(intent_value, jsonFile, indent=10)