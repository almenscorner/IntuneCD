#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains the functions used to get the access token for MS Graph.
"""

import json
import os
from time import sleep

import requests
from cryptography.fernet import Fernet
from msal import ConfidentialClientApplication, PublicClientApplication

AUTHORITY = "https://login.microsoftonline.com/"
SCOPE = ["https://graph.microsoft.com/.default"]


def obtain_accesstoken_app(TENANT_NAME, CLIENT_ID, CLIENT_SECRET):
    """
    This function is used to get an access token to MS Graph using client credentials.

    :param TENANT_NAME: The name of the Azure tenant
    :param CLIENT_ID: The ID of the registered Azure AD application
    :param CLIENT_SECRET: Secret of the registered Azure AD application
    :return: The access token
    """

    # Create app instance
    app = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY + TENANT_NAME,
    )

    token = None

    try:
        # Check if token is already cached
        token = app.acquire_token_silent(SCOPE, account=None)

        # If not, get a new token
        if not token:
            token = app.acquire_token_for_client(scopes=SCOPE)
            if not token:
                raise ValueError("No token returned")
            if "error" in token:
                raise ValueError(
                    "Error obtaining access token: " + token["error_description"]
                )

    except (ValueError, Exception) as e:
        raise ValueError(str(e))

    return token


def obtain_accesstoken_cert(TENANT_NAME, CLIENT_ID, THUMBPRINT, KEY_FILE):
    """
    This function is used to get an access token to MS Graph using a certificate.

    :param TENANT_NAME: The name of the Azure tenant
    :param CLIENT_ID: The ID of the registered Azure AD application
    :param THUMBPRINT Thumbprint of the certificate uploaded to Azure AD
    :param KEY_FILE: Path to the private key of the certificate
    :return: The access token
    """

    # Create app instance
    app = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential={
            "thumbprint": THUMBPRINT,
            "private_key": open(KEY_FILE, encoding="utf-8").read(),
        },
        authority=AUTHORITY + TENANT_NAME,
    )

    token = None

    try:
        # Check if token is already cached
        token = app.acquire_token_silent(SCOPE, account=None)

        # If not, get a new token
        if not token:
            token = app.acquire_token_for_client(scopes=SCOPE)
            if not token:
                raise ValueError("No token returned")
            if "error" in token:
                raise ValueError(
                    "Error obtaining access token: " + token["error_description"]
                )

    except (ValueError, Exception) as e:
        raise ValueError(str(e))

    return token


def obtain_accesstoken_interactive(TENANT_NAME, CLIENT_ID, scopes):
    """
    This function is used to get an access token to MS Graph interactivly.

    :param TENANT_NAME: The name of the Azure tenant
    :param CLIENT_ID: The ID of the registered Azure AD application
    :return: The access token
    """

    # Create app instance
    app = PublicClientApplication(
        client_id=CLIENT_ID,
        client_credential=None,
        authority=AUTHORITY + TENANT_NAME,
    )

    token = None

    try:
        # Get the token interactively
        token = app.acquire_token_interactive(
            scopes=scopes, max_age=1200, prompt="select_account"
        )

        if not token:
            raise ValueError("No token returned")
        if "error" in token:
            raise ValueError(
                "Error obtaining access token: " + token["error_description"]
            )

    except (ValueError, Exception) as e:
        raise ValueError(str(e))

    return token


def obtain_azure_token(TENANT_ID: str, PATH: str) -> str:
    """Obtains an access token for use with Azure internal APIs.
       If a key is provided, the refresh token will be encrypted and stored in a cache file.

    Args:
        TENANT_ID (str): ID of the tenant
        PATH (str): Path to the backup folder

    Raises:
        ValueError: If no tenant ID is provided
        TimeoutError: Timed out waiting for token

    Returns:
        str: The access token
    """
    if not TENANT_ID:
        raise ValueError("No tenant ID provided")

    client_id = "1950a258-227b-4e31-a9cf-717495945fc2"
    # refresh_token = os.environ.get("REFRESH_TOKEN")
    key = os.environ.get("KEY")

    def _write_refresh_token(refresh_token):
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(refresh_token.encode("utf-8"))

        with open(f"{PATH}/cache.bin", "wb") as f:
            f.write(cipher_text)

    def _read_refresh_token():
        cipher_suite = Fernet(key)

        if not os.path.exists(f"{PATH}/cache.bin"):
            return None

        with open(f"{PATH}/cache.bin", "rb") as f:
            cipher_text = f.read()

        plain_text = cipher_suite.decrypt(cipher_text)

        token = plain_text.decode()

        return token

    def _get_device_code():
        body = {
            "resource": "74658136-14ec-4630-ad9b-26e160ff0fc6",
            "client_id": client_id,
        }

        try:
            code = requests.post(
                f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/devicecode",
                data=body,
                timeout=60,
            )
            json_code_data = json.loads(code.text)
            print(
                f'Go to {json_code_data["verification_url"]} and enter {json_code_data["user_code"]}'
            )

            body = {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": client_id,
                "code": json_code_data["device_code"],
            }

            return body

        except ValueError as e:
            print("Failed to get device code: ", e)

    refresh_token = _read_refresh_token() if key else None

    if refresh_token:
        body = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": refresh_token,
        }
    else:
        body = _get_device_code()

    try:
        try_count = 0
        while try_count < 10:
            token = requests.post(
                f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/token",
                data=body,
                timeout=60,
            )
            json_token_data = json.loads(token.text)
            sleep(5)
            if body.get("grant_type") == "refresh_token" and token.status_code == 400:
                body = _get_device_code()

            if json_token_data.get("access_token"):
                break
            try_count += 1

        if try_count == 10:
            raise TimeoutError("Timed out waiting for token")

        if key:
            _write_refresh_token(json_token_data["refresh_token"])

        return json_token_data["access_token"]

    except ValueError as e:
        print("Failed to get token: ", e)
