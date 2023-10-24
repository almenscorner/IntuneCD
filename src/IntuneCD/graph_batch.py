#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to batch requests to the Graph Batch endpoint. Two additional functions,
get_object_assignment and get_object_details is used to retrieve the objects assignment and details from
the batch request.
"""

import json

from .graph_request import makeapirequestPost


def batch_request(data, url, extra_url, token, method="GET") -> list:
    """
    Batch request to the Graph API.

    :param data: List of object IDs to get data for
    :param url: MS graph endpoint for the object
    :param extra_url: Used if anything extra is needed for the url such as /assignments or ?$filter
    :param token: OAuth token used for authentication
    :param method: GET or POST
    :return: List of responses from the batch request
    """

    responses = []
    batch_id = 1
    batch_count = 20
    # Split objects into lists of 20
    batch_list = [data[i : i + batch_count] for i in range(0, len(data), batch_count)]

    # Build a body for each ID in the list
    for i, batch in enumerate(batch_list):
        query_data = {"requests": []}
        for b_id in batch:
            body = {"id": batch_id, "method": method, "url": url + b_id + extra_url}

            batch_id += 1
            query_data["requests"].append(body)

        # POST to the graph batch endpoint
        json_data = json.dumps(query_data)
        request = makeapirequestPost(
            "https://graph.microsoft.com/beta/$batch", token, jdata=json_data
        )
        request_data = sorted(request["responses"], key=lambda item: item.get("id"))

        # Append each successful request to responses list
        for resp in request_data:
            if resp["status"] == 200:
                responses.append(resp["body"])

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
