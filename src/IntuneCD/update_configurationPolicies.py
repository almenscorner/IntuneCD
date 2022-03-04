#!/usr/bin/env python3

"""
This module updates all Settings Catalog configurations in Intune if the configuration in Intune differs from the JSON/YAML file.

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

from .graph_request import makeapirequest, makeapirequestPut, makeapirequestPost
from .graph_batch import batch_assignment, get_object_assignment
from .update_assignment import update_assignment, post_assignment_update
from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/configurationPolicies"


def update(path, token, assignment=False):

    ## Set Settings Catalog path
    configpath = path+"/"+"Settings Catalog/"

    if os.path.exists(configpath) == True:
        ## Get configurations policies
        mem_data = makeapirequest(endpoint, token)
        ## Get current assignments
        mem_assignments = batch_assignment(mem_data,'deviceManagement/configurationPolicies/','/assignments',token)

        for filename in os.listdir(configpath):
            file = os.path.join(configpath, filename)
            # If path is Directory, skip
            if os.path.isdir(file):
                continue
            # If file is .DS_Store, skip
            if filename == ".DS_Store":
                continue

            (name, ext) = os.path.splitext(filename)
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

                    data = {'value':''}
                    if mem_data['value']:
                        for val in mem_data['value']:
                            if repo_data['name'] == val['name']:
                                data['value'] = val

                    ## If Filter exists, continue
                    if data['value']:
                        print("-" * 90)
                        ## Get Filter data from Intune
                        mem_policy_data = makeapirequest(endpoint + "/" + data['value']['id'], token)
                        ## Get Filter settings from Intune
                        mem_policy_settings = makeapirequest(endpoint + "/" + data['value']['id'] + "/settings", token)
                        ## Add settings to the data dictionary
                        mem_policy_data['settings'] = mem_policy_settings['value']

                        diff = DeepDiff(mem_policy_data, repo_data, ignore_order=True).get('values_changed', {})

                        ## If any changed values are found, push them to Intune
                        if diff:
                            print("Updating Settings Catalog policy: " + \
                                  name + ", values changed:")
                            for key, value in diff.items():
                                new_val = value['new_value']
                                old_val = value['old_value']
                                print(
                                    f"New Value: {new_val}, Old Value: {old_val}")
                            request_data = json.dumps(repo_data)
                            q_param = None
                            makeapirequestPut(endpoint + "/" + data['value']['id'], token,q_param,request_data,status_code=204)
                        else:
                            print(
                                'No difference found for Settings Catalog policy: ' + name)

                        if assignment == True:
                            mem_assign_obj = get_object_assignment(data['value']['id'],mem_assignments)
                            update = update_assignment(assign_obj,mem_assign_obj,token)
                            if update is not None:
                                request_data = {}
                                request_data['assignments'] = update
                                post_assignment_update(request_data,data['value']['id'],'deviceManagement/configurationPolicies','assign',token)

                    ## If Configuration Policy does not exist, create it and assign
                    else:
                        print("-" * 90)
                        print(
                            "Configuration Policy not found, creating Policy: " + repo_data['name'])
                        repo_data.pop('settingCount', None)
                        request_json = json.dumps(repo_data)
                        post_request = makeapirequestPost(endpoint, token,q_param=None,jdata=request_json,status_code=201)
                        mem_assign_obj = []
                        assignment = update_assignment(assign_obj,mem_assign_obj,token)
                        if assignment is not None:
                            request_data = {}
                            request_data['assignments'] = assignment
                            post_assignment_update(request_data,post_request['id'],'deviceManagement/configurationPolicies','assign',token)
                        print("Configuration Policy created with id: " + post_request['id'])