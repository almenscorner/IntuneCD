#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to get the access token for the tenant.
"""

import json
import os

from .get_accesstoken import (
    obtain_accesstoken_app,
    obtain_accesstoken_cert,
    obtain_accesstoken_interactive,
)


def getAuth(mode, localauth, certauth, interactiveauth, scopes, entra, tenant):
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
            raise ValueError("One or more os.environ variables not set")
        return obtain_accesstoken_cert(TENANT_NAME, CLIENT_ID, THUMBPRINT, KEY_FILE)

    if interactiveauth:
        TENANT_NAME = os.environ.get("TENANT_NAME")
        CLIENT_ID = os.environ.get("CLIENT_ID")

        if not all([TENANT_NAME, CLIENT_ID]):
            raise ValueError("One or more os.environ variables not set")

        return obtain_accesstoken_interactive(TENANT_NAME, CLIENT_ID, scopes)

    if mode:
        if mode == "devtoprod":
            if localauth:
                with open(localauth, encoding="utf-8") as json_data:
                    auth_dict = json.load(json_data)
                tenant_TENANT_NAME = auth_dict["params"][tenant + "_TENANT_NAME"]
                tenant_CLIENT_ID = auth_dict["params"][tenant + "_CLIENT_ID"]
                tenant_CLIENT_SECRET = auth_dict["params"][tenant + "_CLIENT_SECRET"]
                if entra:
                    os.environ["TENANT_ID"] = auth_dict["params"][tenant + "_TENANT_ID"]
                    os.environ["KEY"] = auth_dict["params"].get("KEY")
            else:
                tenant_TENANT_NAME = os.environ.get(tenant + "_TENANT_NAME")
                tenant_CLIENT_ID = os.environ.get(tenant + "_CLIENT_ID")
                tenant_CLIENT_SECRET = os.environ.get(tenant + "_CLIENT_SECRET")
                if entra:
                    os.environ["TENANT_ID"] = os.environ.get(tenant + "_TENANT_ID")
            if not all([tenant_TENANT_NAME, tenant_CLIENT_ID, tenant_CLIENT_SECRET]):
                raise ValueError(
                    "One or more os.environ variables for " + tenant + " not set"
                )

            return obtain_accesstoken_app(
                tenant_TENANT_NAME, tenant_CLIENT_ID, tenant_CLIENT_SECRET
            )

        if mode == "standalone":
            if localauth:
                with open(localauth, encoding="utf-8") as json_data:
                    auth_dict = json.load(json_data)
                TENANT_NAME = auth_dict["params"]["TENANT_NAME"]
                CLIENT_ID = auth_dict["params"]["CLIENT_ID"]
                CLIENT_SECRET = auth_dict["params"]["CLIENT_SECRET"]
                if entra:
                    os.environ["TENANT_ID"] = auth_dict["params"]["TENANT_ID"]
                    os.environ["KEY"] = auth_dict["params"].get("KEY")
            else:
                TENANT_NAME = os.environ.get("TENANT_NAME")
                CLIENT_ID = os.environ.get("CLIENT_ID")
                CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
                if entra:
                    os.environ["TENANT_ID"] = os.environ.get("TENANT_ID")
            if not all([TENANT_NAME, CLIENT_ID, CLIENT_SECRET]):
                raise ValueError("One or more os.environ variables not set")

            return obtain_accesstoken_app(TENANT_NAME, CLIENT_ID, CLIENT_SECRET)
