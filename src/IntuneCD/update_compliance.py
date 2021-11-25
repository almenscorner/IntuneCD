#!/usr/bin/env python3

"""
This module updates all Compliance Polices in Intune if the configuration in Intune differs from the JSON/YAML file.

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

from .graph_request import makeapirequest,makeapirequestPatch,makeapirequestPost
from .get_add_assignments import add_assignment

from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/deviceCompliancePolicies"

def update(path,token,assignment=False):

    ## Set Compliance Policy path
    configpath = path+"/"+"Compliance Policies/Policies/"
    ## If App Configuration path exists, continue
    if os.path.exists(configpath)==True:
        for filename in os.listdir(configpath):
            file = os.path.join(configpath, filename)
            # If path is Directory, skip
            if os.path.isdir(file):
                continue
            # If file is .DS_Store, skip
            if filename == ".DS_Store":
                continue
            
            ## Check which format the file is saved as then open file, load data and set query parameter
            with open(file) as f:
                    if filename.endswith(".yaml"):
                        data = json.dumps(yaml.safe_load(f))
                        repo_data = json.loads(data)
                        q_param = {"$filter":"displayName eq " + "'" + repo_data['displayName'] + "'", "expand":"scheduledActionsForRule($expand=scheduledActionConfigurations)"}
                        
                    elif filename.endswith(".json"):
                        f = open(file)
                        repo_data = json.load(f)
                        q_param = {"$filter":"displayName eq " + "'" + repo_data['displayName'] + "'", "expand":"scheduledActionsForRule($expand=scheduledActionConfigurations)"}

                    ## Create object to pass in to assignment function
                    assign_obj = {}
                    if "assignments" in repo_data:
                        assign_obj['assignments'] = repo_data['assignments']
                    repo_data.pop('assignments', None)
                        
                    ## Get Compliance Policy with query parameter    
                    mem_data = makeapirequest(endpoint,token,q_param)

                    ## If Compliance Policy exists, continue
                    if mem_data['value']:
                        print("-" * 90)
                        pid = mem_data['value'][0]['id']
                        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime'}
                        for k in remove_keys:
                            mem_data['value'][0].pop(k, None)

                        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime','@odata.context','scheduledActionConfigurations@odata.context','scheduledActionsForRule@odata.context'}
                        for k in remove_keys:
                            mem_data['value'][0].pop(k, None)
                            if mem_data['value'][0]['scheduledActionsForRule']:
                                for rule in mem_data['value'][0]['scheduledActionsForRule']:
                                    rule.pop(k, None)
                                for scheduled_config in mem_data['value'][0]['scheduledActionsForRule'][0]['scheduledActionConfigurations']:
                                    scheduled_config.pop(k, None)

                        ## Check if assignment needs updating and apply chanages
                        if assignment == True:
                            add_assignment(endpoint,assign_obj,pid,token)

                        diff = DeepDiff(mem_data['value'][0], repo_data, ignore_order=True, 
                        exclude_paths="root['scheduledActionsForRule'][0]['scheduledActionConfigurations']").get('values_changed',{})

                        ## If any changed values are found, push them to Intune
                        if diff:
                            print("Updating Compliance policy: " + repo_data['displayName'] + ", values changed:")
                            print(*diff.items(), sep='\n')
                            scheduled_actions = repo_data['scheduledActionsForRule']
                            repo_data.pop('scheduledActionsForRule', None)
                            request_data = json.dumps(repo_data)
                            makeapirequestPatch(endpoint + "/" + pid,token,q_param,request_data,status_code=204)
                            repo_data['scheduledActionsForRule'] = scheduled_actions

                        if repo_data['scheduledActionsForRule']:
                            for mem_rule,repo_rule in zip(mem_data['value'][0]['scheduledActionsForRule'],repo_data['scheduledActionsForRule']):
                                rdiff = DeepDiff(mem_rule, repo_rule, ignore_order=True).get('values_changed',{})
                            if rdiff:
                                print("Updating rules for Compliance Policy: " + repo_data['displayName'] + ", values changed:")
                                print(*rdiff.items(), sep='\n')
                                request_data = {
                                    "deviceComplianceScheduledActionForRules": [
                                        {
                                            "ruleName": "PasswordRequired",
                                            "scheduledActionConfigurations":
                                                repo_data['scheduledActionsForRule'][0]['scheduledActionConfigurations']
                                        }
                                    ]
                                }
                                request_json = json.dumps(request_data)
                                makeapirequestPost(endpoint + "/" + pid + "/scheduleActionsForRules",token,q_param,request_json)
                            else:
                                print('No difference in rules found for Compliance policy: ' + repo_data['displayName'])
                        else:
                            print('No difference found for Compliance policy: ' + repo_data['displayName'])


                    ## If Compliance Policy does not exist, create it and assign
                    else:
                        print("-" * 90)
                        print("Compliance Policy not found, creating Policy: " + repo_data['displayName'])
                        request_json = json.dumps(repo_data)
                        post_request = makeapirequestPost(endpoint,token,q_param=None,jdata=request_json,status_code=201)
                        add_assignment(endpoint,assign_obj,post_request['id'],token)
                        print("Compliance Policy created with id: " + post_request['id'])