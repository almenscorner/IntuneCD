#!/usr/bin/env python3

"""
This module backs up Device Configurations in Intune.

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
from .graph_request import makeapirequest

## Set MS Graph endpoint
endpoint = "https://graph.microsoft.com/beta/deviceManagement/deviceConfigurations"

## Get all Device Configurations and save them in specified path
def savebackup(path,output,token):
    
    configpath = path+"/"+"Device Configurations/"
    data = makeapirequest(endpoint,token)

    for profile in data['value']:
        pid = profile['id']
        remove_keys = {'id','createdDateTime','version','lastModifiedDateTime'}
        for k in remove_keys:
            profile.pop(k, None)

        print("Backing up profile: " + profile['displayName'])
        if os.path.exists(configpath)==False:
            os.mkdir(configpath)
            
        ## If profile is custom macOS or iOS, decode the payload
        if ((profile['@odata.type'] == "#microsoft.graph.macOSCustomConfiguration") or (profile['@odata.type'] == "#microsoft.graph.iosCustomConfiguration")):
            decoded = base64.b64decode(profile['payload']).decode('utf-8')

            if os.path.exists(configpath + "mobileconfig/")==False:
                os.makedirs(configpath + "mobileconfig/")
            ## Save decoded payload as .mobileconfig
            f = open(configpath + "mobileconfig/" + profile['payloadFileName'],'w')
            f.write(decoded)
            ## Save Device Configuration as JSON or YAML depending on configured value in "-o"
            if output != "json":
                with open(configpath + profile['displayName']+".yaml",'w') as yamlFile:
                    yaml.dump(profile, yamlFile, sort_keys=False, default_flow_style=False)
            else:
                with open(configpath + profile['displayName']+".json",'w') as jsonFile:
                    json.dump(profile, jsonFile, indent=10)

        ## If Device Configuration is custom Win10 and the OMA settings are encrypted, get them in plain text
        elif profile['@odata.type'] == "#microsoft.graph.windows10CustomConfiguration" and profile['omaSettings'][0]['isEncrypted'] == True:
            
            omas = []
            for setting in profile['omaSettings']:
                if setting['isEncrypted'] == True:
                    decoded_oma = {}
                    oma_value = makeapirequest(endpoint + "/" + pid + "/getOmaSettingPlainTextValue(secretReferenceValueId='" + setting['secretReferenceValueId'] + "')",token)
                    decoded_oma['@odata.type'] = setting['@odata.type']
                    decoded_oma['displayName'] = setting['displayName']
                    decoded_oma['description'] = setting['description']
                    decoded_oma['omaUri'] = setting['omaUri']
                    decoded_oma['value'] = oma_value
                    decoded_oma['isEncrypted'] = False
                    decoded_oma['secretReferenceValueId'] = None
                    decoded_omas = decoded_oma
                    omas.append(decoded_omas)
                elif setting['isEncrypted'] == False:
                    omas.append(setting)

            profile.pop('omaSettings')
            profile['omaSettings'] = omas

            ## Save Device Configuration as JSON or YAML depending on configured value in "-o"
            if output != "json":
                with open(configpath + profile['displayName']+".yaml",'w') as yamlFile:
                    yaml.dump(profile, yamlFile, sort_keys=False, default_flow_style=False)
            else:
                with open(configpath + profile['displayName']+".json",'w') as jsonFile:
                    json.dump(profile, jsonFile, indent=10)

        ## If Device Configuration are not custom, save it as as JSON or YAML depending on configured value in "-o"
        else:
            if output != "json":
                with open(configpath+profile['displayName']+".yaml",'w') as yamlFile:
                    yaml.dump(profile, yamlFile, sort_keys=False, default_flow_style=False)
            else:
                with open(configpath+profile['displayName']+".json",'w') as jsonFile:
                    json.dump(profile, jsonFile, indent=10)