#!/usr/bin/env python3

"""
This module updates all Notification Templates in Intune if the configuration in Intune differs from the JSON/YAML file.

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
from .graph_request import makeapirequest,makeapirequestPatch

from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/notificationMessageTemplates"

def update(path,token):

    ## Set Notification Template path
    configpath = path+"/"+"Compliance Policies/Message Templates/"
    ## If Notification Template path exists, continue
    if os.path.exists(configpath)==True:
        for filename in os.listdir(configpath):
            file = os.path.join(configpath, filename)
            # If path is Directory, skip
            if os.path.isdir(file):
                continue

            ## Check which format the file is saved as then open file, load data and set query parameter
            with open(file) as f:
                    if filename.endswith(".yaml"):
                        data = json.dumps(yaml.safe_load(f))
                        repo_data = json.loads(data)
                        q_param = {"$filter":"displayName eq " + "'" + repo_data['displayName'] + "'"}

                    elif filename.endswith(".json"):
                        f = open(file)
                        repo_data = json.load(f)
                        q_param = {"$filter":"displayName eq " + "'" + repo_data['displayName'] + "'"}
                        
                    ## Get Notification Template with query parameter
                    mem_data = makeapirequest(endpoint,token,q_param)

                    ## If Notification Template exists, continue
                    if mem_data['value']:
                        ## Get Notification Template data from Intune
                        mem_template_data = makeapirequest(endpoint + "/" + mem_data['value'][0]['id'],token)
                        ## Get Notification Template message data from Intune
                        mem_template_localized = makeapirequest(endpoint + "/" + mem_data['value'][0]['id'] + "?$expand=localizedNotificationMessages",token)
                        ## Create dict to compare Intune data with JSON/YAML data
                        repo_template_data = {
                            "displayName": repo_data['displayName'],
                            "brandingOptions": repo_data['brandingOptions'],
                            "roleScopeTagIds": repo_data['roleScopeTagIds']
                        }

                        diff = DeepDiff(mem_template_data, repo_template_data, ignore_order=True).get('values_changed',{})

                        ## If any changed values are found, push them to Intune
                        if diff:
                            print("Updating Message Template: " + mem_template_data['displayName'] + ", values changed:")
                            print(*diff.items(), sep='\n')
                            request_data = json.dumps(repo_template_data)
                            q_param = None
                            makeapirequestPatch(endpoint + "/" + mem_template_data['id'],token,q_param,request_data)
                        else:
                            print("No difference found for Message Template: " + mem_template_data['displayName'])

                        ## Check each configured locale on the Notification Template for changes
                        for mem_locale,repo_locale in zip(mem_template_localized['localizedNotificationMessages'], repo_data['localizedNotificationMessages']):
                            del mem_locale['lastModifiedDateTime']
                            remove_keys = ('lastModifiedDateTime', 'id', 'locale')
                            for k in remove_keys:     
                                repo_locale.pop(k, None)

                            diff = DeepDiff(mem_locale, repo_locale, ignore_order=True).get('values_changed',{})

                            ## If any changed values are found, push them to Intune
                            if diff:
                                print("Updating Message Template locale: " + mem_locale['locale'] + " for " + mem_template_data['displayName'] + ", values changed")
                                print(*diff.items(), sep='\n')
                                request_data = json.dumps(repo_locale)
                                q_param = None
                                makeapirequestPatch(endpoint + "/" + mem_template_data['id'] + "/" + "localizedNotificationMessages" + "/" + mem_locale['id'],token,q_param,request_data)
                            else:
                                print("No difference in locale " + mem_locale['locale'] + " found for Message Teamplate: " + mem_template_data['displayName'])