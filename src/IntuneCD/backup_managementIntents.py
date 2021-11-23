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

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .get_add_assignments import get_assignments

## Set MS Graph base endpoint
baseEndpoint = "https://graph.microsoft.com/beta/deviceManagement"

## Get all Intents and save them in specified path
def savebackup(path,output,token):
    configpath = path+"/"+"Management Intents/"
    intents = makeapirequest(baseEndpoint + "/intents",token)

    for intent in intents['value']:
        if intent['templateId'] == None:
            continue
        else:
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
                for setting in intent_settings['value']:
                    setting.pop('id', None)
                settings_delta = intent_settings['value']

            intent_value = {
                "displayName": intent['displayName'],
                "description": intent['description'],
                "templateId": intent['templateId'],
                "settingsDelta": settings_delta,
                "roleScopeTagIds": intent['roleScopeTagIds']
            }

            ## Get assignments of Intent
            get_assignments(baseEndpoint + "/intents",intent_value,intent['id'],token)

            ## Get filename without illegal characters
            fname = clean_filename(intent['displayName'])
            ## Save Intent as JSON or YAML depending on configured value in "-o"
            if output != "json":
                with open(configpath+fname+".yaml",'w') as yamlFile:
                    yaml.dump(intent_value, yamlFile, sort_keys=False, default_flow_style=False)
            else:
                with open(configpath+fname+".json",'w') as jsonFile:
                    json.dump(intent_value, jsonFile, indent=10)