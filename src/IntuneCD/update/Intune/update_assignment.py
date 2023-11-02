#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains the functions used to update assignments in Intune.
"""

import json
import uuid

from deepdiff import DeepDiff

from ...intunecdlib.graph_request import makeapirequest, makeapirequestPost


def get_added_removed(diff_object) -> list:
    """
    This function is used to get added and removed assignments from the diff object.

    :param diff_object: Object to check for added assignments
    :return: string of added and removed assignments
    """

    update = []
    for root in diff_object:
        intent = ""
        filterID = ""
        filterType = ""
        target = ""

        if "intent" in diff_object[root]:
            intent = diff_object[root]["intent"]

        if "target" in diff_object[root]:
            if (
                "deviceAndAppManagementAssignmentFilterId"
                in diff_object[root]["target"]
            ):
                filterID = diff_object[root]["target"][
                    "deviceAndAppManagementAssignmentFilterId"
                ]

            if (
                "deviceAndAppManagementAssignmentFilterType"
                in diff_object[root]["target"]
            ):
                filterType = diff_object[root]["target"][
                    "deviceAndAppManagementAssignmentFilterType"
                ]

            if (
                diff_object[root]["target"]["@odata.type"]
                == "#microsoft.graph.groupAssignmentTarget"
            ):
                target = diff_object[root]["target"]["groupId"]

            if (
                diff_object[root]["target"]["@odata.type"]
                == "#microsoft.graph.allDevicesAssignmentTarget"
            ):
                target = "All Devices"

            if (
                diff_object[root]["target"]["@odata.type"]
                == "#microsoft.graph.allLicensedUsersAssignmentTarget"
            ):
                target = "All Users"

        update.append(
            f"intent: {intent}, Filter ID: {filterID}, Filter Type: {filterType}, target: {target}"
        )

    return update


def update_assignment(repo, mem, token, create_groups) -> list:
    """
    This function is used to update assignments for configurations in Intune.

    :param repo: Configuration data from repo
    :param mem: Configuration data from Intune
    :param token: OAuth token used for authentication
    :return: If update is true, return repo data, else return None
    """

    diff = DeepDiff(mem, repo, ignore_order=True)
    added = diff.get("iterable_item_added", {})
    update = False

    if not diff:
        return None

    for val in repo:
        # Request group id based on group name
        if "groupName" in val["target"]:
            request = makeapirequest(
                "https://graph.microsoft.com/beta/groups",
                token,
                {"$filter": "displayName eq " + "'" + val["target"]["groupName"] + "'"},
            )
            if request["value"]:
                val["target"].pop("groupName")
                val["target"].pop("groupType", None)
                val["target"].pop("membershipRule", None)
                val["target"]["groupId"] = request["value"][0]["id"]
            else:
                if create_groups:
                    group_data = {
                        "description": "Created by IntuneCD",
                        "displayName": val["target"]["groupName"],
                        "securityEnabled": True,
                        "mailEnabled": False,
                        "mailNickname": uuid.uuid4().hex,
                    }
                    if val["target"]["groupType"] == "DynamicMembership":
                        group_data["groupTypes"] = ["DynamicMembership"]
                        group_data["membershipRule"] = val["target"]["membershipRule"]
                        group_data["membershipRuleProcessingState"] = "On"

                    request = makeapirequestPost(
                        "https://graph.microsoft.com/beta/groups",
                        token,
                        None,
                        json.dumps(group_data),
                        201,
                    )
                    val["target"].pop("groupName")
                    val["target"].pop("groupType", None)
                    val["target"].pop("membershipRule", None)
                    val["target"]["groupId"] = request["id"]

        # Request filter id based on filter name
        if val["target"]["deviceAndAppManagementAssignmentFilterId"]:
            filters = makeapirequest(
                "https://graph.microsoft.com/beta/deviceManagement/assignmentFilters",
                token,
            )
            for intune_filter in filters["value"]:
                if (
                    val["target"]["deviceAndAppManagementAssignmentFilterId"]
                    == intune_filter["displayName"]
                ):
                    val["target"][
                        "deviceAndAppManagementAssignmentFilterId"
                    ] = intune_filter["id"]

            # If filter is None, remove keys
            if val["target"]["deviceAndAppManagementAssignmentFilterId"] is None:
                val["target"].pop("deviceAndAppManagementAssignmentFilterId")
                val["target"].pop("deviceAndAppManagementAssignmentFilterType")

        if (
            "groupId" in val["target"]
            or "#microsoft.graph.allDevicesAssignmentTarget"
            in val["target"]["@odata.type"]
            or "#microsoft.graph.allLicensedUsersAssignmentTarget"
            in val["target"]["@odata.type"]
        ):
            update = True

    if update is True:
        # Print added assignments
        added = {
            key: value
            for key, value in added.items()
            if "target" in value and "groupName" not in value["target"]
        }
        if added:
            print("Updating assignments, added assignments:")
            updates = get_added_removed(added)
            for update in updates:
                print(update)
            return repo
        return None


def post_assignment_update(
    assignment_object, a_id, url, extra_url, token, status_code=200
):
    """
    This function is used to post assignment update to Intune.

    :param object: Assignment object for configuration
    :param id: id of the configuration to update
    :param url: Graph endpoint to configuration
    :param extra_url: Used if any extra url is needed such as /assign
    :param token: OAuth token used for authentication
    :param status_code: Used if assignment response is not 200
    :return:
    """

    request_json = json.dumps(assignment_object)
    url = f"https://graph.microsoft.com/beta/{url}/{a_id}/{extra_url}"
    makeapirequestPost(
        url, token, q_param=None, jdata=request_json, status_code=status_code
    )
