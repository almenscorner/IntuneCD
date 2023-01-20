#!/usr/bin/env python3

"""
This module contains the functions used to get the access token for MS Graph.
"""


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
                raise Exception("No token returned")

    except Exception as e:
        raise Exception("Error obtaining access token: " + str(e))

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
            "private_key": open(KEY_FILE).read(),
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
                raise Exception("No token returned")

    except Exception as e:
        raise Exception("Error obtaining access token: " + str(e))

    return token


def obtain_accesstoken_interactive(TENANT_NAME, CLIENT_ID):
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

    # Set the requited scopes
    scopes = [
        "DeviceManagementApps.ReadWrite.All",
        "DeviceManagementConfiguration.ReadWrite.All",
        "DeviceManagementManagedDevices.Read.All",
        "DeviceManagementServiceConfig.ReadWrite.All",
        "Group.Read.All",
        "Policy.ReadWrite.ConditionalAccess",
        "Policy.Read.All",
    ]

    try:
        # Get the token interactively
        token = app.acquire_token_interactive(
            scopes=scopes, max_age=1200, prompt="select_account"
        )

        if not token:
            raise Exception("No token returned")

    except Exception as e:
        raise Exception("Error obtaining access token: " + str(e))

    return token
