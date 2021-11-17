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
from .graph_request import makeapirequest,makeapirequestPatch

from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceAppManagement/managedAppPolicies"

def update(path,token):

    ## Set App Protection path
    configpath = path+"/"+"App Protection/"
    ## If App Configuration path exists, continue
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
                        
                    ## Get App Protection with query parameter
                    mem_data = makeapirequest(endpoint,token,q_param)

                    ## If App Protection exists, continue
                    if mem_data['value']:
                        pid = mem_data['value'][0]['id']
                        # Remove keys before using DeepDiff
                        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime'}
                        for k in remove_keys:
                            mem_data['value'][0].pop(k, None)

                        diff = DeepDiff(mem_data['value'][0], repo_data, ignore_order=True).get('values_changed',{})

                        ## If any changed values are found, push them to Intune
                        if diff:
                            print("Updating App protection: " + repo_data['displayName'] + ", values changed:")
                            print(*diff.items(), sep='\n')
                            request_data = json.dumps(repo_data)
                            makeapirequestPatch(endpoint + "/" + pid,token,q_param,request_data,status_code=204)
                        else:
                            print('No difference found for App protection: ' + repo_data['displayName'])