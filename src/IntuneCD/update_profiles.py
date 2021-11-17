#!/usr/bin/env python3

"""
This module updates all Device Configurations in Intune if the configuration in Intune differs from the JSON/YAML file.

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
import plistlib
from .graph_request import makeapirequest,makeapirequestPatch

from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/deviceConfigurations"
patchEndpoint = "https://graph.microsoft.com/v1.0/deviceManagement/deviceConfigurations/"

def update(path,token):

    ## Set Device Configurations path
    configpath = path+"/"+"Device Configurations/"
    ## If Device Configurations path exists, continue
    if os.path.exists(configpath)==True:
        for filename in os.listdir(configpath):
            file = os.path.join(configpath, filename)
            ## If path is Directory, skip
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
                    
                    ## Get Device Configuration with query parameter
                    mem_data = makeapirequest(endpoint,token,q_param)

                    ## If Device Configuration exists, continue
                    if mem_data['value']:
                        pid = mem_data['value'][0]['id']
                        ## Remove keys before using DeepDiff
                        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime'}
                        for k in remove_keys:
                            mem_data['value'][0].pop(k, None)

                        ## If Device Condifguration is custom macOS or iOS, compare the .mobileconfig
                        if ((repo_data['@odata.type'] == "#microsoft.graph.macOSCustomConfiguration") or (repo_data['@odata.type'] == "#microsoft.graph.iosCustomConfiguration")):
                            if os.path.exists(configpath + "mobileconfig/" + repo_data['payloadFileName']):
                                with open(configpath + "mobileconfig/" + repo_data['payloadFileName'], 'rb') as f:
                                    repo_payload_config = plistlib.load(f)

                                decoded = base64.b64decode(mem_data['value'][0]['payload']).decode('utf-8')
                                f = open(configpath + 'temp.mobileconfig','w')
                                f.write(decoded)
                                with open(configpath + 'temp.mobileconfig', 'rb') as f:
                                    mem_payload_config = plistlib.load(f)

                                pdiff = DeepDiff(mem_payload_config, repo_payload_config, ignore_order=True).get('values_changed',{})
                                cdiff = DeepDiff(mem_data['value'][0], repo_data, ignore_order=True, exclude_paths="root['payload']").get('values_changed',{})

                                ## If any changed values are found, push them to Intune
                                if pdiff or cdiff:
                                    print("Updating profile: " + repo_data['displayName'] + ", values changed:")
                                    print(*pdiff.items(), sep='\n')
                                    print(*cdiff.items(), sep='\n')
                                    payload = plistlib.dumps(repo_payload_config)
                                    repo_data['payload'] = str(base64.b64encode(payload),'utf-8')
                                    request_data = json.dumps(repo_data)
                                    makeapirequestPatch(patchEndpoint + pid,token,q_param,request_data,status_code=204)
                                else:
                                    print('No difference found for profile: ' + repo_data['displayName'])

                                os.remove(configpath + 'temp.mobileconfig')

                            else:
                                print("No mobileconfig found for profile: " + repo_data['displayName'])

                        ## If Device Configuration is custom Win10, compare the OMA settings
                        elif mem_data['value'][0]['@odata.type'] == "#microsoft.graph.windows10CustomConfiguration":
                            print("Checking if Win10 Custom Profile: " + repo_data['displayName'] + " has any upates")
                            omas = []
                            for setting in mem_data['value'][0]['omaSettings']:
                                if setting['isEncrypted'] == True:
                                    decoded_oma = {}
                                    oma_value = makeapirequest(endpoint + "/" + pid + "/getOmaSettingPlainTextValue(secretReferenceValueId='" + setting['secretReferenceValueId'] + "')",token)
                                    decoded_oma['@odata.type'] = setting['@odata.type']
                                    decoded_oma['displayName'] = setting['displayName']
                                    decoded_oma['description'] = setting['description']
                                    decoded_oma['omaUri'] = setting['omaUri']
                                    decoded_oma['value'] = oma_value
                                    decoded_oma['isEncrypted'] = True
                                    decoded_oma['secretReferenceValueId'] = None
                                    omas.append(decoded_oma)
                                elif setting['isEncrypted'] == False:
                                    omas.append(setting)

                            mem_data['value'][0].pop('omaSettings')
                            mem_data['value'][0]['omaSettings'] = omas

                            repo_omas = []
                            for mem_omaSetting, repo_omaSetting in zip(mem_data['value'][0]['omaSettings'], repo_data['omaSettings']):

                                diff = DeepDiff(mem_omaSetting, repo_omaSetting, ignore_order=True, exclude_paths="root['isEncrypted']").get('values_changed',{})

                                ## If any changed values are found, push them to Intune
                                if diff:
                                    print("Updating oma setting: " + repo_omaSetting['omaUri'] + ", values changed:")
                                    print(*diff.items(), sep='\n')
                                    if type(repo_omaSetting['value']) is dict:
                                        remove_keys = {'isReadOnly','secretReferenceValueId','isEncrypted'}
                                        for k in remove_keys:
                                            repo_omaSetting.pop(k, None)
                                        repo_omaSetting['value'] = repo_omaSetting['value']['value']
                                        repo_omas.append(repo_omaSetting)
                                    else:
                                        remove_keys = {'isReadOnly','secretReferenceValueId','isEncrypted'}
                                        for k in remove_keys:
                                            repo_omaSetting.pop(k, None)
                                        repo_omas.append(repo_omaSetting)

                            repo_data.pop('omaSettings')
                            repo_data['omaSettings'] = repo_omas

                            if repo_omas:
                                request_data = json.dumps(repo_data)
                                makeapirequestPatch(patchEndpoint + pid,token,q_param,request_data,status_code=204)

                        ## If Device Configuration is not custom, compare the values           
                        else:
                            diff = DeepDiff(mem_data['value'][0], repo_data, ignore_order=True).get('values_changed',{})

                            ## If any changed values are found, push them to Intune
                            if diff:
                                print("Updating profile: " + repo_data['displayName'] + ", values changed:")
                                print(*diff.items(), sep='\n')
                                request_data = json.dumps(repo_data)
                                makeapirequestPatch(patchEndpoint + pid,token,q_param,request_data,status_code=204)
                            else:
                                print('No difference found for profile: ' + repo_data['displayName'])