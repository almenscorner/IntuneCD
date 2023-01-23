#!/usr/bin/env python3

"""
This module is used to get the access token for the tenant.
"""

import json
import os
import subprocess
import json

from .get_accesstoken import (
    obtain_accesstoken_app,
    obtain_accesstoken_cert,
    obtain_accesstoken_interactive,
)


def getAuth(mode, localauth, certauth, interactiveauth, tenant):
    """
    This function authenticates to MS Graph and returns the access token.

    :param mode: The mode used when using this tool
    :param localauth: Path to dict with keys to authenticate
    :param tenant: Which tenant to authenticate to, PROD or DEV
    :return: The access token
    """

    if certauth:
        KEY_FILE = os.environ.get("KEY_FILE")
        THUMBPRINT = os.environ.get("THUMBPRINT")
        TENANT_NAME = os.environ.get("TENANT_NAME")
        CLIENT_ID = os.environ.get("CLIENT_ID")

        if not all([KEY_FILE, THUMBPRINT, TENANT_NAME, CLIENT_ID]):
            raise Exception("One or more os.environ variables not set")
        return obtain_accesstoken_cert(TENANT_NAME, CLIENT_ID, THUMBPRINT, KEY_FILE)

    if interactiveauth:
        TENANT_NAME = os.environ.get("TENANT_NAME")
        CLIENT_ID = os.environ.get("CLIENT_ID")

        if not all([TENANT_NAME, CLIENT_ID]):
            raise Exception("One or more os.environ variables not set")

        return obtain_accesstoken_interactive(TENANT_NAME, CLIENT_ID)

    if mode:
        if mode == "devtoprod":
            if localauth:
                with open(localauth) as json_data:
                    auth_dict = json.load(json_data)
                tenant_TENANT_NAME = auth_dict["params"][tenant + "_TENANT_NAME"]
                tenant_CLIENT_ID = auth_dict["params"][tenant + "_CLIENT_ID"]
                tenant_CLIENT_SECRET = auth_dict["params"][tenant + "_CLIENT_SECRET"]
            else:
                tenant_TENANT_NAME = os.environ.get(tenant + "_TENANT_NAME")
                tenant_CLIENT_ID = os.environ.get(tenant + "_CLIENT_ID")
                tenant_CLIENT_SECRET = os.environ.get(tenant + "_CLIENT_SECRET")
            if not all([tenant_TENANT_NAME, tenant_CLIENT_ID, tenant_CLIENT_SECRET]):
                raise Exception(
                    "One or more os.environ variables for " + tenant + " not set"
                )

            return obtain_accesstoken_app(
                tenant_TENANT_NAME, tenant_CLIENT_ID, tenant_CLIENT_SECRET
            )

        elif mode == "standalone":

            if localauth:
                with open(localauth) as json_data:
                    auth_dict = json.load(json_data)
                TENANT_NAME = auth_dict["params"]["TENANT_NAME"]
                CLIENT_ID = auth_dict["params"]["CLIENT_ID"]
                CLIENT_SECRET = auth_dict["params"]["CLIENT_SECRET"]
            else:
                TENANT_NAME = os.environ.get("TENANT_NAME")
                CLIENT_ID = os.environ.get("CLIENT_ID")
                CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
            if not all([TENANT_NAME, CLIENT_ID, CLIENT_SECRET]):
                raise Exception("One or more os.environ variables not set")

            return obtain_accesstoken_app(TENANT_NAME, CLIENT_ID, CLIENT_SECRET)
