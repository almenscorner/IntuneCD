#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to batch requests to the Graph Batch endpoint. Two additional functions,
get_object_assignment and get_object_details is used to retrieve the objects assignment and details from
the batch request.
"""

import json
import time

from .graph_request import makeapirequestPost
from .logger import log


def create_batch_request(batch, batch_id, method, url, extra_url) -> tuple:
    """Creates a batch request for the Graph API.

    Args:
        batch (list): List of objects
        batch_id (str): ID for the batch request
        method (str): HTTP method to use
        url (str): MS graph endpoint for the object
        extra_url (str): Used if anything extra is needed for the url such as /assignments or ?$filter

    Returns:
        tuple: Tuple containing the query data and the batch ID
    """
    query_data = {"requests": []}
    for b_id in batch:
        body = {"id": batch_id, "method": method, "url": url + b_id + extra_url}
        batch_id += 1
        query_data["requests"].append(body)

    return query_data, batch_id


def handle_responses(
    initial_request_data, request_data, responses, retry_pool
) -> tuple:
    """Handle the responses from the batch request.

    Args:
        initial_request_data (list): List of initial requests
        request_data (list): List of responses from the batch request
        responses (list): List of responses from the batch request
        retry_pool (list): List of failed requests

    Returns:
        tuple: Tuple containing the responses, retry pool and wait time
    """
    wait_time = 0
    for resp in request_data:
        failed_batch_requests = []
        if resp["status"] == 200:
            responses.append(resp["body"])
            retry_pool = [req for req in retry_pool if req["id"] != int(resp["id"])]
        elif resp["status"] in [429, 503]:
            if initial_request_data:
                failed_batch_requests = [
                    i
                    for i in initial_request_data
                    if i["id"] == int(resp["id"]) and i not in retry_pool
                ]
            retry_pool += failed_batch_requests

        wait_time = max(wait_time, int(resp["headers"].get("Retry-After", 0)))

    return responses, retry_pool, wait_time


def create_batch_list(data, batch_count) -> list:
    """Create a list of batches from the data.

    Args:
        data (list): List of objects
        batch_count (int): Number of objects to include in each batch

    Returns:
        list: List of batches
    """
    return [data[i : i + batch_count] for i in range(0, len(data), batch_count)]


def process_batch(
    batch,
    batch_id,
    method,
    url,
    extra_url,
    token,
    initial_request_data,
    responses,
    retry_pool,
) -> tuple:
    """Process the batch request.

    Args:
        batch (list): List of objects
        batch_id (str): ID for the batch request
        method (str): HTTP method to use
        url (str): MS graph endpoint for the object
        extra_url (str): Used if anything extra is needed for the url such as /assignments or ?$filter
        token (str): OAuth token used for authentication
        initial_request_data (list): List of initial requests
        responses (list): List of responses from the batch request
        retry_pool (list): List of failed requests

    Returns:
        tuple: Tuple containing the batch ID, responses, retry pool and wait time
    """
    query_data, batch_id = create_batch_request(batch, batch_id, method, url, extra_url)
    json_data = json.dumps(query_data)
    request = makeapirequestPost(
        "https://graph.microsoft.com/beta/$batch", token, jdata=json_data
    )
    request_data = sorted(request["responses"], key=lambda item: item.get("id"))
    initial_request_data += query_data["requests"]
    responses, retry_pool, wait_time = handle_responses(
        initial_request_data, request_data, responses, retry_pool
    )
    return batch_id, responses, retry_pool, wait_time


def retry_failed_requests(
    retry_pool,
    wait_time,
    max_retries,
    max_wait_time,
    token,
    initial_request_data,
    responses,
    batch_count,
) -> tuple:
    """Retry failed requests.

    Args:
        retry_pool (list): List of failed requests
        wait_time (int): Time to wait before retrying
        max_retries (int): Maximum number of retries
        max_wait_time (int): Maximum time to wait before retrying
        token (str): OAuth token used for authentication
        initial_request_data (list): List of initial requests
        responses (list): List of responses from the batch request
        batch_count (int): Number of objects to include in each batch

    Returns:
        list: List of responses from the batch request
    """
    retry_count = 0
    failed_retry_requests = []
    while retry_count < max_retries and retry_pool:
        log(
            "retry_failed_requests",
            f"Retrying failed requests, retry pool count: {str(len(retry_pool))}",
        )
        if wait_time > 0:
            log("retry_failed_requests", f"Sleeping for {str(wait_time)} seconds...")
            time.sleep(wait_time)
            wait_time = min(wait_time * 2, max_wait_time)
        else:
            log(
                "retry_failed_requests",
                "No wait time in headers, sleeping for 20 seconds...",
            )
            time.sleep(20)
        batch_list = [
            retry_pool[i : i + batch_count]
            for i in range(0, len(retry_pool), batch_count)
        ]
        for batch in batch_list:
            batch_data = {"requests": list(batch)}
            json_data = json.dumps(batch_data)
            request = makeapirequestPost(
                "https://graph.microsoft.com/beta/$batch", token, jdata=json_data
            )
            request_data = sorted(request["responses"], key=lambda item: item.get("id"))
            responses, retry_pool, _ = handle_responses(
                initial_request_data, request_data, responses, retry_pool
            )
            failed_retry_requests = [
                r for r in request["responses"] if r["status"] != 200
            ]
        retry_count += 1
        log("retry_failed_requests", f"Retry count: {str(retry_count)}")
        if retry_pool and retry_count == max_retries:
            break
    log(
        "retry_failed_requests",
        f"Failed requests after {str(retry_count)} retries: {str(len(failed_retry_requests))}",
    )
    return responses


def batch_request(data, url, extra_url, token, method="GET") -> list:
    """Batch request to the Graph API.

    Args:
        data (list): List of objects
        url (str): MS graph endpoint for the object
        extra_url (str): Used if anything extra is needed for the url such as /assignments or ?$filter
        token (str): OAuth token used for authentication
        method (str): HTTP method to use

    Returns:
        list: List of responses from the batch request
    """
    responses = []
    batch_id = 1
    batch_count = 20
    retry_pool = []
    wait_time = 0
    initial_request_data = []

    batch_list = create_batch_list(data, batch_count)
    for batch in batch_list:
        batch_id, responses, retry_pool, wait_time = process_batch(
            batch,
            batch_id,
            method,
            url,
            extra_url,
            token,
            initial_request_data,
            responses,
            retry_pool,
        )

    max_retries = 10
    max_wait_time = 60
    if retry_pool:
        responses = retry_failed_requests(
            retry_pool,
            wait_time,
            max_retries,
            max_wait_time,
            token,
            initial_request_data,
            responses,
            batch_count,
        )

    return responses


def get_group_names(responses, group_ids, token):
    """get all group names."""
    group_responses = batch_request(
        group_ids,
        "groups/",
        "?$select=displayName,id,groupTypes,membershipRule",
        token,
    )
    for value in responses:
        if value is None or "value" not in value:
            continue

        for val in value["value"]:
            if "groupId" not in val["target"]:
                continue

            for g_id in group_responses:
                if g_id.get("id") == val["target"]["groupId"]:
                    val["target"]["groupName"] = g_id.get("displayName", "")
                    if "DynamicMembership" in g_id.get("groupTypes", []):
                        val["target"]["groupType"] = "DynamicMembership"
                        val["target"]["membershipRule"] = g_id.get(
                            "membershipRule", None
                        )
                    else:
                        val["target"]["groupType"] = "StaticMembership"
                    break


def get_filter_name(val, filter_responses):
    """Get the name of the filter."""
    for f_id in filter_responses:
        if f_id["id"] == val["target"]["deviceAndAppManagementAssignmentFilterId"]:
            val["target"]["deviceAndAppManagementAssignmentFilterId"] = f_id[
                "displayName"
            ]
            break


def get_filter_names(responses, filter_ids, token):
    """Get all filter names."""
    filter_ids = [i for i in filter_ids if i != "00000000-0000-0000-0000-000000000000"]
    filter_responses = batch_request(
        filter_ids,
        "deviceManagement/assignmentFilters/",
        "?$select=displayName",
        token,
    )
    for value in responses:
        if value["value"]:
            for val in value["value"]:
                if "deviceAndAppManagementAssignmentFilterId" in val["target"]:
                    get_filter_name(val, filter_responses)


def batch_assignment(data, url, extra_url, token, app_protection=False) -> list:
    """
    Batch request to the Graph API.

    :param data: List of objects
    :param url: MS graph endpoint for the object
    :param extra_url: Used if anything extra is needed for the url such as /assignments or ?$filter
    :param token: OAuth token used for authentication
    :param app_protection: By default False, set to true when getting assignments for APP to get the platform
    :return: List of responses from the batch request
    """

    data_ids = []
    group_ids = []
    filter_ids = []

    # If getting App Protection Assignments, get the platform
    if app_protection is True:
        for a_id in data["value"]:
            if (
                a_id["@odata.type"]
                == "#microsoft.graph.mdmWindowsInformationProtectionPolicy"
            ):
                data_ids.append(f"mdmWindowsInformationProtectionPolicies/{a_id['id']}")
            if (
                a_id["@odata.type"]
                == "#microsoft.graph.windowsInformationProtectionPolicy"
            ):
                data_ids.append(f"windowsInformationProtectionPolicies/{a_id['id']}")
            else:
                data_ids.append(
                    f"{str(a_id['@odata.type']).split('.')[2]}s/{a_id['id']}"
                )
    # Else, just add the objects ID to the list
    else:
        for a_id in data["value"]:
            data_ids.append(a_id["id"])
    # If we have any IDs, batch request the assignments
    if data_ids:
        responses = batch_request(data_ids, url, extra_url, token)
        if not responses:
            return

        if extra_url == "?$expand=assignments":
            response_values = []
            for value in responses:
                if value:
                    response_values.append(
                        {
                            "value": value["assignments"],
                            "@odata.context": value["assignments@odata.context"],
                        }
                    )
            responses = response_values

        group_ids = [
            val
            for list in responses
            if list and "value" in list
            for val in list["value"]
            for keys, val in val.items()
            if "target" in keys
            for keys, val in val.items()
            if "groupId" in keys
        ]
        filter_ids = [
            val
            for list in responses
            if list and "value" in list
            for val in list["value"]
            for keys, val in val.items()
            if "target" in keys
            for keys, val in val.items()
            if "deviceAndAppManagementAssignmentFilterId" in keys
            if val is not None
        ]

        # Batch get name of the groups
        if group_ids:
            get_group_names(responses, group_ids, token)

        # Batch get name of the Filters
        if filter_ids:
            get_filter_names(responses, filter_ids, token)

        return responses


def batch_intents(data, token) -> dict:
    """
    Batch request to the Graph API.

    :param data: List of objects
    :param token: OAuth token used for authentication
    :return: List of responses from the batch request
    """

    base_url = "deviceManagement"
    template_ids = []
    settings_id = []
    categories_responses = []
    settings_responses = []
    intent_values = {"value": []}

    # Get each template ID
    filtered_data = [
        val
        for list in data["value"]
        for key, val in list.items()
        if "templateId" in key and val is not None
    ]
    template_ids = list(dict.fromkeys(filtered_data))

    # Batch get all categories from templates
    if template_ids:
        categories_responses = batch_request(
            template_ids, f"{base_url}/templates/", "/categories", token
        )

    # Build ID for requesting settings for each Intent
    if categories_responses:
        for intent in data["value"]:
            settings_ids = [
                val
                for list in categories_responses
                if intent["templateId"] is not None
                and intent["templateId"] in list["@odata.context"]
                for val in list["value"]
                for keys, val in val.items()
                if "id" in keys
            ]
            for setting_id in settings_ids:
                settings_id.append(f"{intent['id']}/categories/{setting_id}")

    # Batch get all settings for all Intents
    if settings_id:
        settings_responses = batch_request(
            settings_id, f"{base_url}/intents/", "/settings", token
        )

    # If the Intent ID is in the responses, save the settings to settingsDelta for the Intent
    if settings_responses:
        for intent in data["value"]:
            settingsDelta = [
                val
                for list in settings_responses
                if intent["id"] in list["@odata.context"]
                for val in list["value"]
            ]
            intent_values["value"].append(
                {
                    "id": intent["id"],
                    "displayName": intent["displayName"],
                    "description": intent["description"],
                    "templateId": intent["templateId"],
                    "settingsDelta": settingsDelta,
                    "roleScopeTagIds": intent["roleScopeTagIds"],
                }
            )

    return intent_values


def get_object_assignment(o_id, responses) -> list:
    """
    Get the object assignment for the object ID.

    :param o_id: Id of the object to get the assignment for
    :param responses: List of responses from the batch request
    :return: List of assignments for the object
    """

    remove_keys = {"id", "groupId", "sourceId"}
    assignments_list = [
        val
        for list in responses
        if list and "value" in list
        if o_id in list["@odata.context"]
        for val in list["value"]
    ]
    for value in assignments_list:
        for k in remove_keys:
            value.pop(k, None)
            value["target"].pop(k, None)

    return assignments_list


def get_object_details(o_id, responses) -> list:
    """
    Get the object details for the object ID.

    :param o_id: Id of the object to get the details for
    :param responses: List of responses from the batch request
    :return: List of details for the object
    """

    details = [
        val
        for list in responses
        if o_id in list["@odata.context"]
        for val in list["value"]
    ]
    return details
