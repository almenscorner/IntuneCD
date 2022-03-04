#!/usr/bin/env python3

"""
This module updates all App Configuration polices in Intune if the configuration in Intune differs from the JSON/YAML file.
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

from .graph_request import makeapirequest, makeapirequestPatch
from deepdiff import DeepDiff

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/depOnboardingSettings/"

def update(path, token):

    ## Set Apple Enrollment Profile path
    configpath = path+"/"+"Enrollment Profiles/Apple/"
    ## If Apple Enrollment Profile path exists, continue
    if os.path.exists(configpath) == True:
        ## Get IDs of all Apple Enrollment Profiles and add them to a list
        ids = []
        mem_data_accounts = makeapirequest(endpoint, token)
        for id in mem_data_accounts['value']:
            ids.append(id['id'])

        for profile in ids:
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
                            q_param = {"$filter": "displayName eq " +
                                "'" + repo_data['displayName'] + "'"}

                        elif filename.endswith(".json"):
                            f = open(file)
                            repo_data = json.load(f)
                            q_param = {"$filter": "displayName eq " + "'" + repo_data['displayName'] + "'"}

                        ## Get Apple Enrollment Profile with query parameter
                        profile_data = makeapirequest(
                            endpoint + profile + '/enrollmentProfiles', token, q_param)

                        ## If Apple Enrollment Profile exists, continue
                        if profile_data['value']:
                            print("-" * 90)
                            pid = profile_data['value'][0]['id']
                            ## Remove keys before using DeepDiff
                            remove_keys = {'id', 'createdDateTime','version','lastModifiedDateTime'}
                            for k in remove_keys:
                                profile_data['value'][0].pop(k, None)

                            diff = DeepDiff(profile_data['value'][0], repo_data, ignore_order=True).get('values_changed', {})

                            ## If any changed values are found, push them to Intune
                            if diff:
                                print("Updating Apple Enrollment profile: " + \
                                      repo_data['displayName'] + ", values changed:")
                                for key, value in diff.items():
                                    setting = re.search(
                                        "\[(.*)\]", key).group(1)
                                    new_val = value['new_value']
                                    old_val = value['old_value']
                                    print(
                                        f"Setting: {setting}, New Value: {new_val}, Old Value: {old_val}")
                                request_data = json.dumps(repo_data)
                                q_param = None
                                makeapirequestPatch(endpoint + profile + "/enrollmentProfiles/" + pid, token,q_param,request_data,status_code=204)
                            else:
                                print('No difference found for Apple Enrollment profile: ' + repo_data['displayName'])