#!/usr/bin/env python3

"""
This module backs up Group Policy Configurations in Intune.

Parameters
----------
path : str
    The path to save the backup to
output : str
    The format the backup will be saved as
token : str
    The token to use for authenticating the request
"""

import json
import os
import base64
import yaml

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .graph_batch import batch_assignment, get_object_assignment

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/groupPolicyConfigurations"

## Get all Group Policy Configurations and save them in specified path
def savebackup(path, output, exclude, token):

    configpath = path+"/"+"Group Policy Configurations/"
    data = makeapirequest(endpoint, token)

    assignment_responses = batch_assignment(data,f'deviceManagement/groupPolicyConfigurations/','/assignments',token)

    for profile in data['value']:

        definition_endpoint = f"{endpoint}/{profile['id']}/definitionValues?$expand=definition"
        # Get definitions
        definitions = makeapirequest(definition_endpoint, token)

        if definitions:

            profile['definitionValues'] = definitions['value']

            for definition in profile['definitionValues']:
                presentation_endpoint = f"{endpoint}/{profile['id']}/definitionValues/{definition['id']}/presentationValues?$expand=presentation"
                presentation = makeapirequest(presentation_endpoint, token)
                definition['presentationValues'] = presentation['value']

        if "assignments" not in exclude:
            assignments = get_object_assignment(profile['id'],assignment_responses)
            if assignments:
                profile['assignments'] = assignments

        pid = profile['id']
        remove_keys = {'id', 'createdDateTime', 'version',
                       'lastModifiedDateTime', 'sourceId', 'supportsScopeTags'}
        for k in remove_keys:
            profile.pop(k, None)

        print("Backing up profile: " + profile['displayName'])
        if os.path.exists(configpath) == False:
            os.makedirs(configpath)

        ## Get filename without illegal characters
        fname = clean_filename(profile['displayName'])

        if output != "json":
            with open(configpath+'/'+fname+".yaml", 'w') as yamlFile:
                yaml.dump(profile, yamlFile, sort_keys=False,
                            default_flow_style=False)
        else:
            with open(configpath+'/'+fname+".json", 'w') as jsonFile:
                json.dump(profile, jsonFile, indent=10)