#!/usr/bin/env python3

"""
This module updates all App Protection Polices in Intune if the configuration in Intune differs from the JSON/YAML file.

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
from .graph_batch import batch_assignment,get_object_assignment
from .update_assignment import update_assignment,post_assignment_update
from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/"


def update(path, token, assignment=False):

    ## Set App Protection path
    configpath = path+"/"+"App Protection/"
    ## If App Configuration path exists, continue
    if os.path.exists(configpath) == True:

        ## Get App Protections
        mem_data = makeapirequest(f'{endpoint}managedAppPolicies', token)
        ## Get current assignments
        mem_assignments = batch_assignment(mem_data,'deviceAppManagement/','/assignments',token,app_protection=True)

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

                    if repo_data:
                        if repo_data['@odata.type'] == "#microsoft.graph.mdmWindowsInformationProtectionPolicy":
                            platform = "mdmWindowsInformationProtectionPolicies"
                        elif repo_data['@odata.type'] == "#microsoft.graph.windowsInformationProtectionPolicy":
                            platform = "windowsInformationProtectionPolicies"
                        else:
                            platform = f"{str(repo_data['@odata.type']).split('.')[2]}s"

                    ## Create object to pass in to assignment function
                    assign_obj = {}
                    if "assignments" in repo_data:
                        assign_obj = repo_data['assignments']
                    repo_data.pop('assignments', None)

                    ## If App Protection exists, continue
                    data = {'value':''}
                    if mem_data['value']:
                        for val in mem_data['value']:
                            if 'targetedAppManagementLevels' in val and 'targetedAppManagementLevels' in repo_data:
                                if repo_data['targetedAppManagementLevels'] == val['targetedAppManagementLevels'] and \
                                    repo_data['displayName'] == val['displayName']:
                                    data['value'] = val
                            elif repo_data['@odata.type'] == val['@odata.type'] and \
                                repo_data['displayName'] == val['displayName']:
                                data['value'] = val
                                
                    if data['value']:
                        print("-" * 90)
                        mem_id = data['value']['id']
                        platform=""
                        # Remove keys before using DeepDiff
                        remove_keys = {'id', 'createdDateTime','version','lastModifiedDateTime'}
                        for k in remove_keys:
                            data['value'].pop(k, None)

                        diff = DeepDiff(data['value'], repo_data, ignore_order=True).get('values_changed', {})

                        ## If any changed values are found, push them to Intune
                        if diff:
                            print("Updating App protection: " + \
                                  repo_data['displayName'] + ", values changed:")
                            for key, value in diff.items():
                                setting = re.search("\[(.*)\]", key).group(1)
                                new_val = value['new_value']
                                old_val = value['old_value']
                                print(
                                    f"Setting: {setting}, New Value: {new_val}, Old Value: {old_val}")
                            request_data = json.dumps(repo_data)
                            q_param = None
                            makeapirequestPatch(f'{endpoint}{platform}/{mem_id}', token,q_param,request_data,status_code=204)
                        else:
                            print(
                                'No difference found for App protection: ' + repo_data['displayName'])

                        if assignment == True:
                            mem_assign_obj = get_object_assignment(mem_id,mem_assignments)
                            update = update_assignment(assign_obj,mem_assign_obj,token)
                            if update is not None:
                                request_data = {}
                                request_data['assignments'] = update
                                post_assignment_update(request_data,mem_id,f'deviceAppManagement/{platform}','assign',token,status_code=204)

                    ## If App Protection does not exist, create it and assign
                    else:
                        print("-" * 90)
                        print("App Protection not found, creating policy: " + \
                              repo_data['displayName'])
                        request_json = json.dumps(repo_data)
                        post_request = makeapirequestPost(f'{endpoint}managedAppPolicies', token,q_param=None,jdata=request_json,status_code=201)
                        mem_assign_obj = []
                        assignment = update_assignment(assign_obj,mem_assign_obj,token)
                        if assignment is not None:
                            request_data = {}
                            request_data['assignments'] = assignment
                            post_assignment_update(request_data,post_request['id'],f'deviceAppManagement/{platform}','assign',token,status_code=204)
                        print("App Protection created with id: " + post_request['id'])