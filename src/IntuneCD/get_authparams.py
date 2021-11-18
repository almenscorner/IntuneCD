"""
This module authenticates to MS Graph and returns the access token.

Parameters
----------
mode : str
    The mode used when using this tool
localauth : str
    Path to dict with keys to authenticate
tenant : str
    Which tenant to authenticate to, PROD or DEV
"""

import json
import os
from .get_accesstoken import obtain_accesstoken

resource = "https://graph.microsoft.com"

def getAuth(mode,localauth,tenant):
    if mode == 'devtoprod':

        if localauth:
            with open(localauth) as json_data:
                auth_dict = json.load(json_data)
            tenant_TENANT_NAME = auth_dict['params'][tenant+'_TENANT_NAME']
            tenant_CLIENT_ID = auth_dict['params'][tenant+'_CLIENT_ID']
            tenant_CLIENT_SECRET = auth_dict['params'][tenant+'_CLIENT_SECRET']
        else:
            tenant_TENANT_NAME = os.environ.get(tenant+"_TENANT_NAME")
            tenant_CLIENT_ID = os.environ.get(tenant+"_CLIENT_ID")
            tenant_CLIENT_SECRET = os.environ.get(tenant+"_CLIENT_SECRET")
        if ((tenant_TENANT_NAME is None) or (tenant_CLIENT_ID is None) or (tenant_CLIENT_SECRET is None)):
            raise Exception("One or more os.environ variables for " + tenant + " not set")
        else:
            token = obtain_accesstoken(tenant_TENANT_NAME,tenant_CLIENT_ID,tenant_CLIENT_SECRET,resource)
            return token

    elif mode == 'standalone':

        if localauth:
            with open(localauth) as json_data:
                auth_dict = json.load(json_data)
            TENANT_NAME = auth_dict['params']['TENANT_NAME']
            CLIENT_ID = auth_dict['params']['CLIENT_ID']
            CLIENT_SECRET = auth_dict['params']['CLIENT_SECRET']
        else:
            TENANT_NAME = os.environ.get("TENANT_NAME")
            CLIENT_ID = os.environ.get("CLIENT_ID")
            CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
        if ((TENANT_NAME is None) or (CLIENT_ID is None) or (CLIENT_SECRET is None)):
            raise Exception("One or more os.environ variables not set")
        else:
            token = obtain_accesstoken(TENANT_NAME,CLIENT_ID,CLIENT_SECRET,resource)
            return token