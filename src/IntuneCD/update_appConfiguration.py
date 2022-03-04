#!/usr/bin/env python3

"""
This module updates all App Configuration Polices in Intune if the configuration in Intune differs from the JSON/YAML file.

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
from .update_assignment import update_assignment, post_assignment_update
from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/mobileAppConfigurations"
app_endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"


def update(path, token, assignment=False):

    ## Set App Configuration path
    configpath = path+"/"+"App Configuration/"
    ## If App Configuration path exists, continue
    if os.path.exists(configpath) == True:

        ## Get App Configurations
        mem_data = makeapirequest(endpoint, token)
        ## Get current assignments
        mem_assignments = batch_assignment(
            mem_data, 'deviceAppManagement/mobileAppConfigurations/', '/assignments', token)

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

                    ## If App Configuration exists, continue
                    data = {'value': ''}
                    if mem_data['value']:
                        for val in mem_data['value']:
                            if repo_data['@odata.type'] == val['@odata.type'] and \
                               repo_data['displayName'] == val['displayName']:
                                data['value'] = val

                    if data['value']:
                        print("-" * 90)
                        mem_id = data['value']['id']
                        ## Remove keys before using DeepDiff
                        remove_keys = {'id', 'createdDateTime', 'version', 'lastModifiedDateTime'}
                        for k in remove_keys:
                            data['value'].pop(k, None)
                        repo_data.pop('targetedMobileApps', None)

                        diff = DeepDiff(data['value'], repo_data, ignore_order=True).get(
                            'values_changed', {})

                        ## If any changed values are found, push them to Intune
                        if diff:
                            print("Updating App configuration: " +
                                  repo_data['displayName'] + ", values changed:")
                            for key, value in diff.items():
                                setting = re.search(
                                    "\[(.*)\]", key).group(1).split("[")[-1]
                                new_val = value['new_value']
                                old_val = value['old_value']
                                print(
                                    f"Setting: {setting}, New Value: {new_val}, Old Value: {old_val}")
                            request_data = json.dumps(repo_data)
                            q_param = None
                            makeapirequestPatch(endpoint + "/" + mem_id, token, q_param, request_data,status_code=204)
                        else:
                            print(
                                'No difference found for App configuration: ' + repo_data['displayName'])

                        if assignment == True:
                            mem_assign_obj = get_object_assignment(mem_id, mem_assignments)
                            update = update_assignment(assign_obj, mem_assign_obj,token)
                            if update is not None:
                                request_data = {}
                                request_data['assignments'] = update
                                post_assignment_update(request_data, mem_id,'deviceAppManagement/mobileAppConfigurations/',
                                                        '/microsoft.graph.managedDeviceMobileAppConfiguration/assign',token)

                    ## If App Configuration does not exist, create it and assign
                    else:
                        print("-" * 90)
                        print("App Configuration not found, creating: " +
                              repo_data['displayName'])
                        app_ids = {}
                        ## If backup contains targeted apps, search for the app
                        if repo_data['targetedMobileApps']:
                            q_param = {"$filter": "(isof(" + "'"+str(repo_data['targetedMobileApps']['type']).replace('#', '') + "'" + '))',
                                       "$search": repo_data['targetedMobileApps']['appName']}
                            app_request = makeapirequest(
                                app_endpoint, token, q_param)
                            if app_request['value']:
                                app_ids = app_request['value'][0]['id']
                        ## If the app could be found and matches type and name in backup, continue to create
                        if app_ids:
                            repo_data.pop('targetedMobileApps')
                            repo_data['targetedMobileApps'] = [app_ids]
                            request_json = json.dumps(repo_data)
                            post_request = makeapirequestPost(endpoint, token, q_param=None, jdata=request_json,status_code=201)
                            mem_assign_obj = []
                            assignment = update_assignment(assign_obj, mem_assign_obj,token)
                            if assignment is not None:
                                request_data = {}
                                request_data['assignments'] = assignment
                                post_assignment_update(request_data, post_request['id'],'deviceAppManagement/mobileAppConfigurations/',
                                                        '/microsoft.graph.managedDeviceMobileAppConfiguration/assign',token)
                            print("App Configuration created with id: " +
                                  post_request['id'])
                        else:
                            print("App configured in App Configuration profile could not be found, skipping creation")
