#!/usr/bin/env python3

"""
This module is used to get an access token to MS Graph.

Parameters
----------
TENANT_NAME : str
    The name of the Azure tenant
CLIENT_ID : str
    The ID of the registered Azure AD application
CLIENT_SECRET : str
    Secret of the registered Azure AD application
"""

from adal import AuthenticationContext

from __main__ import *

def obtain_accesstoken(TENANT_NAME,CLIENT_ID,CLIENT_SECRET,resource):
    auth_context = AuthenticationContext('https://login.microsoftonline.com/' +
        TENANT_NAME)
    token = auth_context.acquire_token_with_client_credentials(
        resource=resource,client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET)
    return token