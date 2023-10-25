#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains the functions to make API requests to the Microsoft Graph API.
"""

import json
import time

import requests


def makeapirequest(endpoint, token, q_param=None):
    """
    This function makes a GET request to the Microsoft Graph API.

    :param endpoint: The endpoint to make the request to.
    :param token: The token to use for authenticating the request.
    :param q_param: The query parameters to use for the request.
    :return: The response from the request.
    """

    retry_codes = [504, 502, 503]

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(token["access_token"]),
    }

    if q_param is not None:
        response = requests.get(endpoint, headers=headers, params=q_param, timeout=120)
        if response.status_code in retry_codes:
            print(
                "Ran into issues with Graph request, waiting 10 seconds and trying again..."
            )
            time.sleep(10)
            response = requests.get(endpoint, headers=headers, timeout=120)
        elif response.status_code == 429:
            print(
                f"Hit Graph throttling, trying again after {response.headers['Retry-After']} seconds"
            )
            while response.status_code == 429:
                time.sleep(int(response.headers["Retry-After"]))
                response = requests.get(endpoint, headers=headers, timeout=120)
    else:
        response = requests.get(endpoint, headers=headers, timeout=120)
        if response.status_code in retry_codes:
            retry_count = 0
            while retry_count < 3:
                print(
                    "Ran into issues with Graph request, waiting 10 seconds and trying again..."
                )
                time.sleep(10)
                response = requests.get(endpoint, headers=headers, timeout=120)
                if response.status_code == 200:
                    break
                retry_count += 1
        elif response.status_code == 429:
            print(
                f"Hit Graph throttling, trying again after {response.headers['Retry-After']} seconds"
            )
            while response.status_code == 429:
                time.sleep(int(response.headers["Retry-After"]))
                response = requests.get(endpoint, headers=headers, timeout=120)

    if response.status_code == 200:
        json_data = json.loads(response.text)

        if "@odata.nextLink" in json_data.keys():
            record = makeapirequest(json_data["@odata.nextLink"], token)
            entries = len(record["value"])
            count = 0
            while count < entries:
                json_data["value"].append(record["value"][count])
                count += 1

        return json_data

    if response.status_code == 404:
        print("Resource not found in Microsoft Graph: " + endpoint)
    elif ("assignmentFilters" in endpoint) and ("FeatureNotEnabled" in response.text):
        print("Assignment filters not enabled in tenant, skipping")
    else:
        raise requests.exceptions.HTTPError(
            "Request failed with {} - {}".format(response.status_code, response.text)
        )


def makeapirequestPatch(
    patchEndpoint, token, q_param=None, jdata=None, status_code=200
):
    """
    This function makes a PATCH request to the Microsoft Graph API.

    :param patchEndpoint: The endpoint to make the request to.
    :param token: The token to use for authenticating the request.
    :param q_param: The query parameters to use for the request.
    :param jdata: The JSON data to use for the request.
    :param status_code: The status code to expect from the request.
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(token["access_token"]),
    }

    if q_param is not None:
        response = requests.patch(
            patchEndpoint, headers=headers, params=q_param, data=jdata, timeout=120
        )
    else:
        response = requests.patch(
            patchEndpoint, headers=headers, data=jdata, timeout=120
        )
    if response.status_code == status_code:
        pass
    else:
        raise requests.exceptions.HTTPError(
            "Request failed with {} - {}".format(response.status_code, response.text)
        )


def makeapirequestDelete(
    deleteEndpoint, token, q_param=None, jdata=None, status_code=200
):
    """
    This function makes a DELETE request to the Microsoft Graph API.

    :param deleteEndpoint: The endpoint to make the request to.
    :param token: The token to use for authenticating the request.
    :param q_param: The query parameters to use for the request.
    :param jdata: The JSON data to use for the request.
    :param status_code: The status code to expect from the request.
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(token["access_token"]),
    }

    if q_param is not None:
        response = requests.delete(
            deleteEndpoint, headers=headers, params=q_param, data=jdata, timeout=120
        )
    else:
        response = requests.delete(
            deleteEndpoint, headers=headers, data=jdata, timeout=120
        )
    if response.status_code == status_code:
        pass
    else:
        raise requests.exceptions.HTTPError(
            "Request failed with {} - {}".format(response.status_code, response.text)
        )


def makeapirequestPost(patchEndpoint, token, q_param=None, jdata=None, status_code=200):
    """
    This function makes a POST request to the Microsoft Graph API.

    :param patchEndpoint: The endpoint to make the request to.
    :param token: The token to use for authenticating the request.
    :param q_param: The query parameters to use for the request.
    :param jdata: The JSON data to use for the request.
    :param status_code: The status code to expect from the request.
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(token["access_token"]),
    }

    if q_param is not None:
        response = requests.post(
            patchEndpoint, headers=headers, params=q_param, data=jdata, timeout=120
        )
    else:
        response = requests.post(
            patchEndpoint, headers=headers, data=jdata, timeout=120
        )
    if response.status_code == status_code:
        if response.text:
            json_data = json.loads(response.text)
            return json_data

    elif response.status_code == 504:
        print(
            "Ran into issues with Graph request, waiting 10 seconds and trying again..."
        )
        time.sleep(10)
        response = requests.post(
            patchEndpoint, headers=headers, data=jdata, timeout=120
        )
    elif response.status_code == 429:
        print(
            f"Hit Graph throttling, trying again after {response.headers['Retry-After']} seconds"
        )
        while response.status_code == 429:
            time.sleep(int(response.headers["Retry-After"]))
            response = requests.post(
                patchEndpoint, headers=headers, data=jdata, timeout=120
            )
    else:
        raise requests.exceptions.HTTPError(
            "Request failed with {} - {}".format(response.status_code, response.text)
        )


def makeapirequestPut(patchEndpoint, token, q_param=None, jdata=None, status_code=200):
    """
    This function makes a PUT request to the Microsoft Graph API.

    :param patchEndpoint: The endpoint to make the request to.
    :param token: The token to use for authenticating the request.
    :param q_param: The query parameters to use for the request.
    :param jdata: The JSON data to use for the request.
    :param status_code: The status code to expect from the request.
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(token["access_token"]),
    }

    if q_param is not None:
        response = requests.put(
            patchEndpoint, headers=headers, params=q_param, data=jdata, timeout=120
        )
    else:
        response = requests.put(patchEndpoint, headers=headers, data=jdata, timeout=120)
    if response.status_code == status_code:
        pass
    else:
        raise requests.exceptions.HTTPError(
            "Request failed with {} - {}".format(response.status_code, response.text)
        )
