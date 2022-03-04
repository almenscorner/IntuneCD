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
import re

from .graph_request import makeapirequest, makeapirequestPatch, makeapirequestPost
from .graph_batch import batch_assignment, get_object_assignment
from .update_assignment import update_assignment,post_assignment_update
from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/deviceCompliancePolicies"


def update(path, token, assignment=False):

    ## Set Compliance Policy path
    configpath = path+"/"+"Compliance Policies/Policies/"
    ## If App Configuration path exists, continue
    if os.path.exists(configpath) == True:
        ## Get compliance policies
        q_param = {"expand": "scheduledActionsForRule($expand=scheduledActionConfigurations)"}
        mem_data = makeapirequest(endpoint, token, q_param)
        ## Get current assignments
        mem_assignments = batch_assignment(mem_data,'deviceManagement/deviceCompliancePolicies/','/assignments',token)

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

                    elif filename.endswith(".json"):
                        f = open(file)
                        repo_data = json.load(f)

                    ## Create object to pass in to assignment function
                    assign_obj = {}
                    if "assignments" in repo_data:
                        assign_obj = repo_data['assignments']
                    repo_data.pop('assignments', None)

                    ## If Compliance Policy exists, continue
                    data = {'value':''}
                    if mem_data['value']:
                        for val in mem_data['value']:
                            if repo_data['@odata.type'] == val['@odata.type'] and \
                               repo_data['displayName'] == val['displayName']:
                                data['value'] = val
                                
                    if data['value']:
                        print("-" * 90)
                        mem_id = data['value']['id']
                        remove_keys = {'id', 'createdDateTime','version','lastModifiedDateTime'}
                        for k in remove_keys:
                            data['value'].pop(k, None)

                        remove_keys = {'id', 'createdDateTime','version','lastModifiedDateTime','@odata.context',
                                        'scheduledActionConfigurations@odata.context','scheduledActionsForRule@odata.context'}
                        for k in remove_keys:
                            data['value'].pop(k, None)
                            if data['value']['scheduledActionsForRule']:
                                for rule in data['value']['scheduledActionsForRule']:
                                    rule.pop(k, None)
                                for scheduled_config in data['value']['scheduledActionsForRule'][0]['scheduledActionConfigurations']:
                                    scheduled_config.pop(k, None)

                        diff = DeepDiff(data['value'], repo_data, ignore_order=True,
                        exclude_paths="root['scheduledActionsForRule'][0]['scheduledActionConfigurations']").get('values_changed', {})

                        ## If any changed values are found, push them to Intune
                        if diff:
                            print("Updating Compliance policy: " + \
                                  repo_data['displayName'] + ", values changed:")
                            for key, value in diff.items():
                                setting = re.search("\[(.*)\]", key).group(1)
                                new_val = value['new_value']
                                old_val = value['old_value']
                                print(f"Setting: {setting}, New Value: {new_val}, Old Value: {old_val}")
                                
                            scheduled_actions = repo_data['scheduledActionsForRule']
                            repo_data.pop('scheduledActionsForRule', None)
                            request_data = json.dumps(repo_data)
                            q_param = None
                            makeapirequestPatch(endpoint + "/" + mem_id, token,q_param,request_data,status_code=204)
                            repo_data['scheduledActionsForRule'] = scheduled_actions

                        if repo_data['scheduledActionsForRule']:
                            for mem_rule, repo_rule in zip(data['value']['scheduledActionsForRule'],repo_data['scheduledActionsForRule']):
                                rdiff = DeepDiff(mem_rule, repo_rule, ignore_order=True).get('values_changed', {})
                            if rdiff:
                                print("Updating rules for Compliance Policy: " + \
                                      repo_data['displayName'] + ", values changed:")
                                for key, value in rdiff.items():
                                    setting = re.search(
                                        "\[(.*)\]", key).group(1).split("[")[-1]
                                    new_val = value['new_value']
                                    old_val = value['old_value']
                                    print(
                                        f"Setting: {setting}, New Value: {new_val}, Old Value: {old_val}")
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
                                q_param = None
                                makeapirequestPost(endpoint + "/" + mem_id + "/scheduleActionsForRules", token,q_param,request_json)
                            else:
                                print('No difference in rules found for Compliance policy: ' + repo_data['displayName'])
                        else:
                            print('No difference found for Compliance policy: ' + repo_data['displayName'])

                        if assignment == True:
                            mem_assign_obj = get_object_assignment(mem_id,mem_assignments)
                            update = update_assignment(assign_obj,mem_assign_obj,token)
                            if update is not None:
                                request_data = {}
                                request_data['assignments'] = update
                                post_assignment_update(request_data,mem_id,'deviceManagement/deviceCompliancePolicies','assign',token)

                    ## If Compliance Policy does not exist, create it and assign
                    else:
                        print("-" * 90)
                        print(
                            "Compliance Policy not found, creating Policy: " + repo_data['displayName'])
                        request_json = json.dumps(repo_data)
                        post_request = makeapirequestPost(endpoint, token,q_param=None,jdata=request_json,status_code=201)
                        mem_assign_obj = []
                        assignment = update_assignment(assign_obj,mem_assign_obj,token)
                        if assignment is not None:
                            request_data = {}
                            request_data['assignments'] = assignment
                            post_assignment_update(request_data,post_request['id'],'deviceManagement/deviceCompliancePolicies','assign',token)
                        print("Compliance Policy created with id: " + post_request['id'])