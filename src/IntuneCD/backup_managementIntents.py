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
from .graph_batch import batch_intents, get_object_assignment, batch_assignment

## Set MS Graph base endpoint
baseEndpoint = "https://graph.microsoft.com/beta/deviceManagement"
template_endpoint = "https://graph.microsoft.com/beta/deviceManagement/templates"

## Get all Intents and save them in specified path
def savebackup(path, output, exclude, token):
    configpath = path+"/"+"Management Intents/"
    intents = makeapirequest(baseEndpoint + "/intents", token)
    templates = makeapirequest(template_endpoint,token)

    assignment_responses = batch_assignment(intents,f'deviceManagement/intents/','/assignments',token)
    intent_responses = batch_intents(intents,token)

    if intent_responses:
        for intent_value in intent_responses['value']:
            print("Backing up Intent: " + intent_value['displayName'])

            for template in templates['value']:
                if intent_value['templateId'] == template['id']:
                    template_type = template['displayName']

            configpath = path+"/"+"Management Intents/" + \
                template_type + "/"
            if os.path.exists(configpath) == False:
                os.makedirs(configpath)

            if "assignments" not in exclude:
                assignments = get_object_assignment(intent_value['id'],assignment_responses)
                if assignments:
                    intent_value['assignments'] = assignments

            for setting in intent_value['settingsDelta']:
                setting.pop('id',None)
            intent_value.pop('id',None)

            ## Get filename without illegal characters
            fname = clean_filename(intent_value['displayName'])
            ## Save Intent as JSON or YAML depending on configured value in "-o"
            if output != "json":
                with open(configpath+fname+".yaml", 'w') as yamlFile:
                    yaml.dump(intent_value, yamlFile,
                                sort_keys=False, default_flow_style=False)
            else:
                with open(configpath+fname+".json", 'w') as jsonFile:
                    json.dump(intent_value, jsonFile, indent=10)