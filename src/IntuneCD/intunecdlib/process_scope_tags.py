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

    def _get_scope_tags(scope_tag_key):
        log("get_scope_tags_name", "Checking if scope tags are in the data.")
        # list comprehension to get the scope tag name
        if data.get(scope_tag_key):
            log("get_scope_tags_name", "Scope tags are in the data.")
            data[scope_tag_key] = [
                tag["displayName"]
                for tag in scope_tags
                if tag["id"] in data[scope_tag_key]
            ]
            log("get_scope_tags_name", f"Scope tags: {data[scope_tag_key]}")

    _get_scope_tags("roleScopeTagIds")
    _get_scope_tags("roleScopeTags")

    return data


def get_scope_tags_id(data, scope_tags):
    """
    Get the ID of the scope tag.

    :param data: The data to search for the scope tag ID
    :param scope_tags: The scope tag to search for
    """

    def _get_scope_tags(scope_tag_key):
        log("get_scope_tags_id", "Checking if scope tags are in the data.")
        # list comprehension to get the scope tag name
        if data.get(scope_tag_key):
            log("get_scope_tags_id", "Scope tags are in the data.")
            data[scope_tag_key] = [
                tag["id"]
                for tag in scope_tags
                if tag["displayName"] in data[scope_tag_key]
            ]
            log("get_scope_tags_id", f"Scope tags: {data[scope_tag_key]}")

    _get_scope_tags("roleScopeTagIds")
    _get_scope_tags("roleScopeTags")

    return data
