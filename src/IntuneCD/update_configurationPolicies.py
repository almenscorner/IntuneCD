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

from .graph_request import makeapirequest,makeapirequestPut,makeapirequestPost
from .get_add_assignments import add_assignment

from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/configurationPolicies"

def update(path,token,assignment=False):

    ## Set Settings Catalog path
    configpath = path+"/"+"Settings Catalog/"

    if os.path.exists(configpath)==True:
        for filename in os.listdir(configpath):
            file = os.path.join(configpath, filename)
            # If path is Directory, skip
            if os.path.isdir(file):
                continue
            # If file is .DS_Store, skip
            if filename == ".DS_Store":
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

                    ## Create object to pass in to assignment function
                    assign_obj = {}
                    if "assignments" in repo_data:
                        assign_obj['assignments'] = repo_data['assignments']
                    repo_data.pop('assignments', None)
                        
                    # Get Filter with query parameter    
                    mem_data = makeapirequest(endpoint,token,q_param)

                    ## If Filter exists, continue
                    if mem_data['value']:
                        print("-" * 90)
                        ## Get Filter data from Intune
                        mem_policy_data = makeapirequest(endpoint + "/" + mem_data['value'][0]['id'],token)
                        ## Get Filter settings from Intune
                        mem_policy_settings = makeapirequest(endpoint + "/" + mem_data['value'][0]['id'] + "/settings",token)
                        ## Add settings to the data dictionary
                        mem_policy_data['settings'] = mem_policy_settings['value']

                        ## Check if assignment needs updating and apply chanages
                        if assignment == True:
                            add_assignment(endpoint,assign_obj,mem_data['value'][0]['id'],token)

                        diff = DeepDiff(mem_policy_data, repo_data, ignore_order=True).get('values_changed',{})

                        ## If any changed values are found, push them to Intune
                        if diff:
                            print("Updating Settings Catalog policy: " + name + ", values changed:")
                            print(*diff.items(), sep='\n')
                            request_data = json.dumps(repo_data)
                            makeapirequestPut(endpoint + "/" + mem_data['value'][0]['id'],token,q_param,request_data,status_code=204)
                        else:
                            print('No difference found for Settings Catalog policy: ' + name)

                    ## If Configuration Policy does not exist, create it and assign
                    else:
                        print("-" * 90)
                        print("Configuration Policy not found, creating Policy: " + repo_data['name'])
                        repo_data.pop('settingCount', None)
                        request_json = json.dumps(repo_data)
                        post_request = makeapirequestPost(endpoint,token,q_param=None,jdata=request_json,status_code=201)
                        add_assignment(endpoint,assign_obj,post_request['id'],token)
                        print("Configuration Policy created with id: " + post_request['id'])