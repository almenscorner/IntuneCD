#!/usr/bin/env python3

"""
This module updates all Endpoint Security configurations (intents) in Intune if the configuration in Intune differs from the JSON/YAML file.

Parameters
----------
path : str
    The path to where the backup is saved
token : str
    The token to use for authenticating the request
"""

import json
import os
import yaml
import glob
from .graph_request import makeapirequest,makeapirequestPost

from deepdiff import DeepDiff

## Set MS Graph base endpoint
baseEndpoint = "https://graph.microsoft.com/beta/deviceManagement"

def update(path,token):

    ## Set Intent path
    configpath = path+"/"+"Management Intents/"
    ## If Intents path exists, continue
    if os.path.exists(configpath)==True:
        ## Set glob pattern
        pattern = configpath + "*/*"
        for filename in glob.glob(pattern, recursive=True):

            ## Check which format the file is saved as then open file, load data and set query parameter
            with open(filename) as f:
                    if filename.endswith(".yaml"):
                        data = json.dumps(yaml.safe_load(f))
                        repo_data = json.loads(data)
                        q_param = {"$filter":"displayName eq " + "'" + repo_data['displayName'] + "'"}

                    elif filename.endswith(".json"):
                        f = open(filename)
                        repo_data = json.load(f)
                        q_param = {"$filter":"displayName eq " + "'" + repo_data['displayName'] + "'"}

                    ## Get Intent with query parameter
                    mem_data = makeapirequest(baseEndpoint + "/intents",token,q_param)

                    ## If Intent exists, continue
                    if mem_data['value']:
                        print("Checking if Intent: " + repo_data['displayName'] + " has any upates")
                        ## Get Intent template
                        intent_template = makeapirequest(baseEndpoint + "/templates" + "/" + mem_data['value'][0]['templateId'],token)     
                        configpath = path+"/"+"Management Intents/" + intent_template['displayName'] + "/"
                        ## Get Intent categories
                        intent_template_categories = makeapirequest(baseEndpoint + "/templates" + "/" + mem_data['value'][0]['templateId'] + "/categories",token)

                        ## Create dict for Intent settings
                        settings_delta = {}
                        ## Get settings for each category and add to dict
                        for intent_category in intent_template_categories['value']:
                            intent_settings = makeapirequest(baseEndpoint + "/intents" + "/" + mem_data['value'][0]['id'] + "/categories" + "/" + intent_category['id'] + "/settings",token)
                            settings_delta = intent_settings['value']

                        ## Compare category settings from Intune with JSON/YAML
                        for mem_setting,repo_setting in zip(settings_delta, repo_data['settingsDelta']):
                            diff = DeepDiff(mem_setting, repo_setting, ignore_order=True).get('values_changed',{})

                            ## If any changed values are found, push them to Intune
                            if diff:
                                print("Updating Intent settings: " + repo_setting['definitionId'] + ", values changed:")
                                print(*diff.items(), sep='\n')
                                ## Create dict that we will use as the request json
                                if repo_setting['@odata.type'] == '#microsoft.graph.deviceManagementComplexSettingInstance':
                                    type = "valueJson"
                                    value = repo_setting['valueJson']
                                else:
                                    type = "value"
                                    value = repo_setting['value']
                                settings = {
                                    "settings": [
                                        {
                                            "id": mem_setting['id'],
                                            "definitionId": repo_setting['definitionId'],
                                            "@odata.type": repo_setting['@odata.type'],
                                            type: value 
                                        }
                                    ]
                                }
                                request_data = json.dumps(settings)
                                q_param=None
                                makeapirequestPost(baseEndpoint + "/intents/" + mem_data['value'][0]['id'] + "/updateSettings",token,q_param,request_data,status_code=204)