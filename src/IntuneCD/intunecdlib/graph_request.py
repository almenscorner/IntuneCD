#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains the functions to make API requests to the Microsoft Graph API.
"""

import datetime
import json
import os
import time

import requests

from .logger import log


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


def makeAuditRequest(graph_filter, token):
    """
    This function makes a GET request to the Microsoft Graph API to get the audit logs for a specific object.

    :param pid: The ID of the object to get the audit logs for.
    :param graph_filter: The filter to use for the request.
    :param token: The token to use for authenticating the request.
    """

    audit_data = []
    if not os.getenv("AUDIT_DAYS_BACK"):
        days_back = 1
    else:
        days_back = int(os.getenv("AUDIT_DAYS_BACK"))
    log("makeAuditRequest", f"AUDIT_DAYS_BACK: {days_back}")
    # Get the date and time 24 hours ago and format it
    start_date = datetime.datetime.now() - datetime.timedelta(days=days_back)
    start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    log("makeAuditRequest", f"Start date: {start_date}")
    # Get the current date and time
    end_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    log("makeAuditRequest", f"End date: {end_date}")
    # Create query to get audit logs for the object
    # if not graph_filter:
    #    graph_filter = f"resources/any(s:s/resourceId eq '{pid}')"
    q_param = {
        "$filter": (
            f"{graph_filter} and activityDateTime gt {start_date} and activityDateTime le {end_date} and "
            "activityOperationType ne 'Get'"
        ),
        "$select": "actor,activityDateTime,activityOperationType,activityResult,resources",
        "$orderby": "activityDateTime desc",
    }
    log("makeAuditRequest", f"Query parameters: {q_param}")

    # Make the request to the Microsoft Graph API
    endpoint = "https://graph.microsoft.com/v1.0/deviceManagement/auditEvents"
    data = makeapirequest(endpoint, token, q_param)

    # If there are audit logs, return the latest one
    if data["value"]:
        log("makeAuditRequest", f"Got {len(data['value'])} audit logs.")
        for audit_log in data["value"]:
            # is the actor an app or a user?
            if audit_log["actor"]["auditActorType"] == "ItPro":
                actor = audit_log["actor"].get("userPrincipalName")
            else:
                actor = audit_log["actor"].get("applicationDisplayName")
            log("makeAuditRequest", f"Actor found: {actor}")
            audit_data.append(
                {
                    "resourceId": audit_log["resources"][0]["resourceId"],
                    "auditResourceType": audit_log["resources"][0]["auditResourceType"],
                    "actor": actor,
                    "activityDateTime": audit_log["activityDateTime"],
                    "activityOperationType": audit_log["activityOperationType"],
                    "activityResult": audit_log["activityResult"],
                }
            )

    return audit_data
