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
from .graph_request import makeapirequest,makeapirequestPut

from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/configurationPolicies"

def update(path,token):

    ## Set Settings Catalog path
    configpath = path+"/"+"Settings Catalog/"

    if os.path.exists(configpath)==True:
        for filename in os.listdir(configpath):
            file = os.path.join(configpath, filename)
            # If path is Directory, skip
            if os.path.isdir(file):
                continue
            
            (name,ext) = os.path.splitext(filename)
            ## Check which format the file is saved as then open file, load data and set query parameter
            with open(file) as f:
                    if filename.endswith(".yaml"):
                        data = json.dumps(yaml.safe_load(f))
                        repo_data = json.loads(data)
                        q_param = {"$filter":"name eq " + "'" + name + "'"}

                    elif filename.endswith(".json"):
                        f = open(file)
                        repo_data = json.load(f)
                        q_param = {"$filter":"name eq " + "'" + name + "'"}
                        
                    # Get Filter with query parameter    
                    mem_data = makeapirequest(endpoint,token,q_param)

                    ## If Filter exists, continue
                    if mem_data['value']:
                        ## Get Filter data from Intune
                        mem_policy_data = makeapirequest(endpoint + "/" + mem_data['value'][0]['id'],token)
                        ## Get Filter settings from Intune
                        mem_policy_settings = makeapirequest(endpoint + "/" + mem_data['value'][0]['id'] + "/settings",token)
                        ## Add settings to the data dictionary
                        mem_policy_data['settings'] = mem_policy_settings['value']

                        diff = DeepDiff(mem_policy_data, repo_data, ignore_order=True).get('values_changed',{})

                        ## If any changed values are found, push them to Intune
                        if diff:
                            print("Updating Settings Catalog policy: " + name + ", values changed:")
                            print(*diff.items(), sep='\n')
                            request_data = json.dumps(repo_data)
                            makeapirequestPut(endpoint + "/" + mem_data['value'][0]['id'],token,q_param,request_data,status_code=204)
                        else:
                            print('No difference found for Settings Catalog policy: ' + name)