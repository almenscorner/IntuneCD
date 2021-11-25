#!/usr/bin/env python3

"""
This module updates all Filters in Intune if the configuration in Intune differs from the JSON/YAML file.

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

from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/assignmentFilters"

def update(path,token):

    ## Set Filters path
    configpath = path+"/"+"Filters"
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
                        
                    elif filename.endswith(".json"):
                        f = open(file)
                        repo_data = json.load(f)
                    
                    ## Get Filter with query parameter
                    mem_data = makeapirequest(endpoint,token)
                    filter_value = {}

                    ## If Filter exists, continue
                    if mem_data['value']:
                        for val in mem_data['value']:
                            if repo_data['displayName'] == val['displayName']:
                                filter_value = val
                    if filter_value:
                        print("-" * 90)
                        filter_id = filter_value['id']
                        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime'}
                        for k in remove_keys:
                            filter_value.pop(k, None)

                        diff = DeepDiff(filter_value, repo_data, ignore_order=True).get('values_changed',{})
                            
                        ## If any changed values are found, push them to Intune
                        if diff:
                            print("Updating Filter: " + repo_data['displayName'] + ", values changed:")
                            print(*diff.items(), sep='\n')
                            repo_data.pop("platform", None)
                            request_data = json.dumps(repo_data)
                            makeapirequestPatch(endpoint + "/" + filter_id,token,q_param=None,jdata=request_data)
                        else:
                            print('No difference found for Filter: ' + repo_data['displayName'])

                    ## If Filter does not exist, create it
                    else:
                        print("-" * 90)
                        print("Assignment filter not found, creating filter: " + repo_data['displayName'])
                        request_json = json.dumps(repo_data)
                        post_request = makeapirequestPost(endpoint,token,q_param=None,jdata=request_json,status_code=201)
                        print("Assignemnt filter created with id: " + post_request['id'])