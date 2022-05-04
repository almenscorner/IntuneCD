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
import re

from .graph_request import makeapirequest, makeapirequestPatch, makeapirequestPost
from .graph_batch import batch_assignment, get_object_assignment
from .update_assignment import update_assignment, post_assignment_update
from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/deviceConfigurations"


def update(path, token, assignment=False):

    ## Set Device Configurations path
    configpath = path+"/"+"Device Configurations/"
    ## If Device Configurations path exists, continue
    if os.path.exists(configpath) == True:
        ## Get profiles
        mem_data = makeapirequest(endpoint, token)
        ## Get current assignment
        mem_assignments = batch_assignment(mem_data,'deviceManagement/deviceConfigurations/','/assignments',token)
        
        for filename in os.listdir(configpath):

            file = os.path.join(configpath, filename)
            ## If path is Directory, skip
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
                        repo_data = json.load(f)

                    ## Create object to pass in to assignment function
                    assign_obj = {}
                    if "assignments" in repo_data:
                        assign_obj = repo_data['assignments']
                    repo_data.pop('assignments', None)

                    ## If Device Configuration exists, continue
                    data = {'value':''}
                    if mem_data['value']:
                        ## Updating Windows update rings is currently not supported
                        if repo_data['@odata.type'] == "#microsoft.graph.windowsUpdateForBusinessConfiguration":
                            continue

                        for val in mem_data['value']:
                            if repo_data['@odata.type'] == val['@odata.type'] and \
                               repo_data['displayName'] == val['displayName']:
                                data['value'] = val
                                
                    if data['value']:

                        print("-" * 90)
                        mem_id = data['value']['id']
                        ## Remove keys before using DeepDiff
                        remove_keys = {'id', 'createdDateTime','version','lastModifiedDateTime'}
                        for k in remove_keys:
                            data['value'].pop(k, None)

                        ## If Device Condifguration is custom macOS or iOS, compare the .mobileconfig
                        if ((repo_data['@odata.type'] == "#microsoft.graph.macOSCustomConfiguration") or (repo_data['@odata.type'] == "#microsoft.graph.iosCustomConfiguration")):
                            if os.path.exists(configpath + "mobileconfig/" + repo_data['payloadFileName']):
                                with open(configpath + "mobileconfig/" + repo_data['payloadFileName'], 'rb') as f:
                                    repo_payload_config = plistlib.load(f)

                                decoded = base64.b64decode(
                                    data['value']['payload']).decode('utf-8')
                                f = open(configpath + 'temp.mobileconfig', 'w')
                                f.write(decoded)
                                with open(configpath + 'temp.mobileconfig', 'rb') as f:
                                    mem_payload_config = plistlib.load(f)

                                pdiff = DeepDiff(mem_payload_config, repo_payload_config, ignore_order=True).get('values_changed', {})
                                cdiff = DeepDiff(data['value'], repo_data, ignore_order=True, exclude_paths="root['payload']").get('values_changed', {})

                                ## If any changed values are found, push them to Intune
                                if pdiff or cdiff:
                                    print(
                                        "Updating profile: " + repo_data['displayName'] + ", values changed:")
                                    if pdiff:
                                        for key, value in pdiff.items():
                                            setting = re.search(
                                                "\[(.*)\]", key).group(1).split("[")[-1]
                                            new_val = value['new_value']
                                            old_val = value['old_value']
                                            print(
                                                f"Setting: {setting}, New Value: {new_val}, Old Value: {old_val}")
                                    if cdiff:
                                        for key, value in cdiff.items():
                                            setting = re.search(
                                                "\[(.*)\]", key).group(1)
                                            new_val = value['new_value']
                                            old_val = value['old_value']
                                            print(
                                                f"Setting: {setting}, New Value: {new_val}, Old Value: {old_val}")
                                    payload = plistlib.dumps(
                                        repo_payload_config)
                                    repo_data['payload'] = str(base64.b64encode(payload), 'utf-8')
                                    request_data = json.dumps(repo_data)
                                    q_param = None
                                    makeapirequestPatch(endpoint + "/" + mem_id, token,q_param,request_data,status_code=204)
                                else:
                                    print(
                                        'No difference found for profile: ' + repo_data['displayName'])

                                os.remove(configpath + 'temp.mobileconfig')

                            else:
                                print("No mobileconfig found for profile: " + \
                                    repo_data['displayName'])

                        ## If Device Configuration is custom Win10, compare the OMA settings
                        elif data['value']['@odata.type'] == "#microsoft.graph.windows10CustomConfiguration":
                            print("Checking if Win10 Custom Profile: " + \
                                repo_data['displayName'] + " has any upates")
                            omas = []
                            for setting in data['value']['omaSettings']:
                                if setting['isEncrypted'] == True:
                                    decoded_oma = {}
                                    oma_value = makeapirequest(endpoint + "/" + mem_id + "/getOmaSettingPlainTextValue(secretReferenceValueId='" + setting['secretReferenceValueId'] + "')", token)
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

                            data['value'].pop('omaSettings')
                            data['value']['omaSettings'] = omas

                            repo_omas = []
                            for mem_omaSetting, repo_omaSetting in zip(data['value']['omaSettings'], repo_data['omaSettings']):

                                diff = DeepDiff(mem_omaSetting, repo_omaSetting, ignore_order=True, exclude_paths="root['isEncrypted']").get('values_changed', {})

                                ## If any changed values are found, push them to Intune
                                if diff:
                                    print(
                                        "Updating oma setting: " + repo_omaSetting['omaUri'] + ", values changed:")
                                    for key, value in diff.items():
                                        new_val = value['new_value']
                                        old_val = value['old_value']
                                        print(
                                            f"New Value: {new_val}, Old Value: {old_val}")
                                    if type(repo_omaSetting['value']) is dict:
                                        remove_keys = {'isReadOnly', 'secretReferenceValueId','isEncrypted'}
                                        for k in remove_keys:
                                            repo_omaSetting.pop(k, None)
                                        repo_omaSetting['value'] = repo_omaSetting['value']['value']
                                        repo_omas.append(repo_omaSetting)
                                    else:
                                        remove_keys = {'isReadOnly', 'secretReferenceValueId','isEncrypted'}
                                        for k in remove_keys:
                                            repo_omaSetting.pop(k, None)
                                        repo_omas.append(repo_omaSetting)

                            repo_data.pop('omaSettings')
                            repo_data['omaSettings'] = repo_omas

                            if repo_omas:
                                request_data = json.dumps(repo_data)
                                q_param = None
                                makeapirequestPatch(endpoint + "/" + mem_id, token,q_param,request_data,status_code=204)

                        ## If Device Configuration is not custom, compare the values
                        else:
                            diff = DeepDiff(data['value'], repo_data, ignore_order=True).get('values_changed', {})

                            ## If any changed values are found, push them to Intune
                            if diff:
                                print(
                                    "Updating profile: " + repo_data['displayName'] + ", values changed:")
                                for key, value in diff.items():
                                    setting = re.search(
                                        "\[(.*)\]", key).group(1)
                                    new_val = value['new_value']
                                    old_val = value['old_value']
                                    print(
                                        f"Setting: {setting}, New Value: {new_val}, Old Value: {old_val}")
                                request_data = json.dumps(repo_data)
                                q_param = None
                                makeapirequestPatch(endpoint + "/" + mem_id, token,q_param,request_data,status_code=204)
                            else:
                                print('No difference found for profile: ' + \
                                    repo_data['displayName'])

                        if assignment == True:
                            mem_assign_obj = get_object_assignment(mem_id,mem_assignments)
                            update = update_assignment(assign_obj,mem_assign_obj,token)
                            if update is not None:
                                request_data = {}
                                request_data['assignments'] = update
                                post_assignment_update(request_data,mem_id,'deviceManagement/deviceConfigurations','assign',token)

                    ## If profile does not exist, create it and assign
                    else:
                        ## If profile is custom win10, create correct omaSettings format before posting
                        if repo_data['@odata.type'] == "#microsoft.graph.windows10CustomConfiguration":
                            repo_omas = []
                            for repo_omaSetting in repo_data['omaSettings']:
                                if type(repo_omaSetting['value']) is dict:
                                    remove_keys = {'isReadOnly', 'secretReferenceValueId','isEncrypted'}
                                    for k in remove_keys:
                                        repo_omaSetting.pop(k, None)
                                    repo_omaSetting['value'] = repo_omaSetting['value']['value']
                                    repo_omas.append(repo_omaSetting)
                                else:
                                    remove_keys = {'isReadOnly', 'secretReferenceValueId','isEncrypted'}
                                    for k in remove_keys:
                                        repo_omaSetting.pop(k, None)
                                    repo_omas.append(repo_omaSetting)
                            repo_data.pop('omaSettings')
                            repo_data['omaSettings'] = repo_omas
                        ## Post new profile
                        print("-" * 90)
                        print("Profile not found, creating profile: " + \
                              repo_data['displayName'])
                        request_json = json.dumps(repo_data)
                        post_request = makeapirequestPost(endpoint, token,q_param=None,jdata=request_json,status_code=201)
                        mem_assign_obj = []
                        assignment = update_assignment(assign_obj,mem_assign_obj,token)
                        if assignment is not None:
                            request_data = {}
                            request_data['assignments'] = assignment
                            post_assignment_update(request_data,post_request['id'],'deviceManagement/deviceConfigurations','assign',token)
                        print("Profile created with id: " + post_request['id'])