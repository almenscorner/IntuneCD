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
from .graph_request import makeapirequest,makeapirequestPatch

from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/deviceManagementScripts"

def update(path,token):

    ## Set Powershell script path
    configpath = path+"/"+"Scripts/Powershell"
    ## If Powershell script path exists, continue
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

                    ## Get Powershell script with query parameter
                    mem_powershellScript = makeapirequest(endpoint,token,q_param)

                    ## If Powershell script exists, continue
                    if mem_powershellScript['value']:
                        q_param = None
                        ## Get Powershell script details
                        mem_data = makeapirequest(endpoint + "/" + mem_powershellScript['value'][0]['id'],token,q_param)
                        pid = mem_data['id']
                        ## Remove keys before using DeepDiff
                        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime'}
                        for k in remove_keys:
                            mem_data.pop(k, None)

                        ## Check if script data is saved and read the file
                        if os.path.exists(configpath + "/Script Data/" + repo_data['fileName']):
                            with open(configpath + "/Script Data/" + repo_data['fileName'], 'r') as f:
                                repo_payload_config = f.read()

                            mem_payload_config = base64.b64decode(mem_data['scriptContent']).decode('utf-8')

                            pdiff = DeepDiff(mem_payload_config, repo_payload_config, ignore_order=True).get('values_changed',{})
                            cdiff = DeepDiff(mem_data, repo_data, ignore_order=True, exclude_paths="root['scriptContent']").get('values_changed',{})

                            ## If any changed values are found, push them to Intune
                            if pdiff or cdiff:
                                print("Updating Powershell script: " + repo_data['displayName'] + ", values changed:")
                                if pdiff:
                                    print("Script changed, check commit history for change details")
                                print(*cdiff.items(), sep='\n')
                                powershell_bytes = repo_payload_config.encode('utf-8')
                                repo_data['scriptContent'] = base64.b64encode(powershell_bytes).decode('utf-8')
                                request_data = json.dumps(repo_data)
                                makeapirequestPatch(endpoint + "/" + pid,token,q_param,request_data)
                            else:
                                print('No difference found for Powershell script: ' + repo_data['displayName'])