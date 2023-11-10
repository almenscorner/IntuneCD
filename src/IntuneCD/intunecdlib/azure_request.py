# -*- coding: utf-8 -*-
import json
from uuid import uuid4

import requests

BASE_URL = "https://main.iam.ad.ext.azure.com/api/"


def make_azure_request(token, api_endpoint, q_param=None) -> dict:
    """Make a request to the Azure API.

    Args:
        token (str): The token to use for authenticating the request.
        api_endpoint (str): The endpoint to make the request to.
        q_param (str, optional): Query parameter to use. Defaults to None.

    Raises:
        requests.exceptions.HTTPError: If the request fails.

    Returns:
        dict: The response from the request.
    """
    header = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-ms-client-request-id": str(uuid4()),
        "x-ms-correlation-id": str(uuid4()),
        "host": "main.iam.ad.ext.azure.com",
    }

    if q_param:
        response = requests.get(
            f"{BASE_URL}{api_endpoint}", headers=header, params=q_param
        )
    else:
        response = requests.get(f"{BASE_URL}{api_endpoint}", headers=header)

    if response.status_code == 200:
        return json.loads(response.text)
    if response.status_code == 404:
        print(f"Resource not found in Azure: {api_endpoint}")
    else:
        raise requests.exceptions.HTTPError(
            f"Failed to get data from {api_endpoint} - {response.text}"
        )


def make_azure_request_put(token, api_endpoint, data, q_param=None, status_code=204):
    """Make a request to the Azure API.

    Args:
        token (str): The token to use for authenticating the request.
        api_endpoint (str): The endpoint to make the request to.
        q_param (str, optional): Query parameter to use. Defaults to None.
        status_code (int, optional): The status code to expect from the request. Defaults to 204.

    Raises:
        requests.exceptions.HTTPError: If the request fails.
    """
    header = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-ms-client-request-id": str(uuid4()),
        "x-ms-correlation-id": str(uuid4()),
        "host": "main.iam.ad.ext.azure.com",
    }

    if q_param:
        response = requests.put(
            f"{BASE_URL}{api_endpoint}", headers=header, params=q_param, data=data
        )
    else:
        response = requests.put(f"{BASE_URL}{api_endpoint}", headers=header, data=data)

    if response.status_code == status_code:
        pass
    else:
        raise requests.exceptions.HTTPError(
            f"Failed to post data {api_endpoint} - {response.text}"
        )


def make_azure_request_post(token, api_endpoint, data, q_param=None, status_code=204):
    """Make a request to the Azure API.

    Args:
        token (str): The token to use for authenticating the request.
        api_endpoint (str): The endpoint to make the request to.
        q_param (str, optional): Query parameter to use. Defaults to None.
        status_code (int, optional): The status code to expect from the request. Defaults to 204.

    Raises:
        requests.exceptions.HTTPError: If the request fails.
    """
    header = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-ms-client-request-id": str(uuid4()),
        "x-ms-correlation-id": str(uuid4()),
        "host": "main.iam.ad.ext.azure.com",
    }

    if q_param:
        response = requests.post(
            f"{BASE_URL}{api_endpoint}", headers=header, params=q_param, data=data
        )
    else:
        response = requests.post(f"{BASE_URL}{api_endpoint}", headers=header, data=data)

    if response.status_code == status_code:
        pass
    else:
        raise requests.exceptions.HTTPError(
            f"Failed to post data {api_endpoint} - {response.text}"
        )


def make_azure_request_patch(token, api_endpoint, data, q_param=None, status_code=204):
    """Make a request to the Azure API.

    Args:
        token (str): The token to use for authenticating the request.
        api_endpoint (str): The endpoint to make the request to.
        q_param (str, optional): Query parameter to use. Defaults to None.
        status_code (int, optional): The status code to expect from the request. Defaults to 204.

    Raises:
        requests.exceptions.HTTPError: If the request fails.
    """
    header = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-ms-client-request-id": str(uuid4()),
        "x-ms-correlation-id": str(uuid4()),
        "host": "main.iam.ad.ext.azure.com",
    }

    if q_param:
        response = requests.patch(
            f"{BASE_URL}{api_endpoint}", headers=header, params=q_param, data=data
        )
    else:
        response = requests.patch(
            f"{BASE_URL}{api_endpoint}", headers=header, data=data
        )

    if response.status_code == status_code:
        pass
    else:
        raise requests.exceptions.HTTPError(
            f"Failed to post data {api_endpoint} - {response.text}"
        )
