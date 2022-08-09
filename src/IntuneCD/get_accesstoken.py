#!/usr/bin/env python3

"""
This module contains the functions used to get the access token for MS Graph.
"""

from adal import AuthenticationContext


def obtain_accesstoken(TENANT_NAME, CLIENT_ID, CLIENT_SECRET, resource):
    """
    This function is used to get an access token to MS Graph.

    :param TENANT_NAME: The name of the Azure tenant
    :param CLIENT_ID: The ID of the registered Azure AD application
    :param CLIENT_SECRET: Secret of the registered Azure AD application
    :param resource: The resource to get an access token for
    :return: The access token
    """

    auth_context = AuthenticationContext('https://login.microsoftonline.com/' +
                                         TENANT_NAME)
    token = auth_context.acquire_token_with_client_credentials(
        resource=resource, client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET)
    return token
