#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module processes the audit data from Intune.
"""

from .graph_request import makeapirequest
from .logger import log


def get_scope_tags(token):
    """
    Get scope tags from Intune.

    :param token: Token to use for authenticating the request
    """
    endpoint = "https://graph.microsoft.com/beta/deviceManagement/roleScopeTags"
    data = makeapirequest(endpoint, token)
    return data["value"]


def get_scope_tags_name(data, scope_tags):
    """
    Get the name of the scope tag.

    :param data: The data to search for the scope tag name
    :param scope_tags: The scope tag to search for
    """

    log("get_scope_tags_name", "Checking if scope tags are in the data.")
    if data.get("roleScopeTagIds"):
        log("get_scope_tags_name", "Scope tags are in the data.")
        # list comprehension to get the scope tag name
        data["roleScopeTagIds"] = [
            tag["displayName"]
            for tag in scope_tags
            if tag["id"] in data["roleScopeTagIds"]
        ]
        log("get_scope_tags_name", f"Scope tags: {data['roleScopeTagIds']}")

    return data


def get_scope_tags_id(data, scope_tags):
    """
    Get the ID of the scope tag.

    :param data: The data to search for the scope tag ID
    :param scope_tags: The scope tag to search for
    """

    log("get_scope_tags_id", "Checking if scope tags are in the data.")
    if data.get("roleScopeTagIds"):
        log("get_scope_tags_id", "Scope tags are in the data.")
        # list comprehension to get the scope tag ID
        data["roleScopeTagIds"] = [
            tag["id"]
            for tag in scope_tags
            if tag["displayName"] in data["roleScopeTagIds"]
        ]
        log("get_scope_tags_id", f"Scope tags: {data['roleScopeTagIds']}")

    return data
