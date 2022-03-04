#!/usr/bin/env python3

"""
This module updates all Powershell scripts in Intune if the configuration in Intune differs from the JSON/YAML file.

Parameters
----------
path : str
    The path to where the backup is saved
token : str
    The token to use for authenticating the request
"""

import json
import os
import base64
import yaml
import re

from .graph_request import makeapirequest, makeapirequestPatch, makeapirequestPost
from .graph_batch import batch_assignment, get_object_assignment
from .update_assignment import update_assignment, post_assignment_update
from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/deviceManagementScripts"


def update(path, token, assignment=False):

    ## Set Powershell script path
    configpath = path+"/"+"Scripts/Powershell"
    ## If Powershell script path exists, continue
    if os.path.exists(configpath) == True:
        ## Get scripts
        mem_powershellScript = makeapirequest(endpoint, token)
        ## Get current assignment
        mem_assignments = batch_assignment(mem_powershellScript,'deviceManagement/deviceManagementScripts/','/assignments',token)

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

                    data = {'value':''}
                    if mem_powershellScript['value']:
                        for val in mem_powershellScript['value']:
                            if repo_data['displayName'] == val['displayName']:
                                data['value'] = val

                    ## If Powershell script exists, continue
                    if data['value']:
                        print("-" * 90)
                        ## Get Powershell script details
                        mem_data = makeapirequest(endpoint + "/" + data['value']['id'], token)
                        mem_id = mem_data['id']
                        ## Remove keys before using DeepDiff
                        remove_keys = {'id', 'createdDateTime','version','lastModifiedDateTime'}
                        for k in remove_keys:
                            mem_data.pop(k, None)

                        ## Check if script data is saved and read the file
                        if os.path.exists(configpath + "/Script Data/" + repo_data['fileName']):
                            with open(configpath + "/Script Data/" + repo_data['fileName'], 'r') as f:
                                repo_payload_config = f.read()

                            mem_payload_config = base64.b64decode(
                                mem_data['scriptContent']).decode('utf-8')

                            pdiff = DeepDiff(mem_payload_config, repo_payload_config, ignore_order=True).get('values_changed', {})
                            cdiff = DeepDiff(mem_data, repo_data, ignore_order=True, exclude_paths="root['scriptContent']").get('values_changed', {})

                            ## If any changed values are found, push them to Intune
                            if pdiff or cdiff:
                                print("Updating Powershell script: " + repo_data['displayName'] + ", values changed:")
                                if cdiff:
                                    for key, value in cdiff.items():
                                        setting = re.search(
                                            "\[(.*)\]", key).group(1)
                                        new_val = value['new_value']
                                        old_val = value['old_value']
                                        print(
                                            f"Setting: {setting}, New Value: {new_val}, Old Value: {old_val}")
                                if pdiff:
                                    print(
                                        "Script changed, check commit history for change details")
                                powershell_bytes = repo_payload_config.encode(
                                    'utf-8')
                                repo_data['scriptContent'] = base64.b64encode(
                                    powershell_bytes).decode('utf-8')
                                request_data = json.dumps(repo_data)
                                q_param = None
                                makeapirequestPatch(endpoint + "/" + mem_id, token,q_param,request_data)
                            else:
                                print(
                                    'No difference found for Powershell script: ' + repo_data['displayName'])

                        if assignment == True:
                            mem_assign_obj = get_object_assignment(mem_id,mem_assignments)
                            update = update_assignment(assign_obj,mem_assign_obj,token)
                            if update is not None:
                                request_data = {}
                                request_data['deviceManagementScriptAssignments'] = update
                                post_assignment_update(request_data,mem_id,'deviceManagement/deviceManagementScripts','assign',token)

                    ## If Powershell script does not exist, create it and assign
                    else:
                        print("-" * 90)
                        print(
                            "Powershell script not found, creating script: " + repo_data['displayName'])
                        request_json = json.dumps(repo_data)
                        post_request = makeapirequestPost(endpoint, token,q_param=None,jdata=request_json,status_code=201)
                        mem_assign_obj = []
                        assignment = update_assignment(assign_obj,mem_assign_obj,token)
                        if assignment is not None:
                            request_data = {}
                            request_data['deviceManagementScriptAssignments'] = assignment
                            post_assignment_update(request_data,post_request['id'],'deviceManagement/deviceManagementScripts','assign',token)
                        print("Powershell script created with id: " + post_request['id'])