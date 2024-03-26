# -*- coding: utf-8 -*-
from .BaseGraphModule import BaseGraphModule


class ProcessScopeTags(BaseGraphModule):
    """Process scope tags from Intune."""

    def __init__(
        self,
        token: str = None,
    ):
        """Initializes the ProcessScopeTags class"""
        self.token = token

    def get_scope_tags(self):
        """
        Get scope tags from Intune.

        :param token: Token to use for authenticating the request
        """
        endpoint = "https://graph.microsoft.com/beta/deviceManagement/roleScopeTags"
        data = self.make_graph_request(endpoint)
        return data["value"]

    def get_scope_tags_name(self, data, scope_tags):
        """
        Get the name of the scope tag.

        :param data: The data to search for the scope tag name
        :param scope_tags: The scope tag to search for
        """

        def _get_scope_tags(self, scope_tag_key):
            self.log(
                function="get_scope_tags_name",
                msg="Checking if scope tags are in the data.",
            )
            # list comprehension to get the scope tag name
            if data.get(scope_tag_key):
                self.log(
                    function="get_scope_tags_name", msg="Scope tags are in the data."
                )
                data[scope_tag_key] = [
                    tag["displayName"]
                    for tag in scope_tags
                    if tag["id"] in data[scope_tag_key]
                ]
                self.log(
                    function="get_scope_tags_name",
                    msg=f"Scope tags: {data[scope_tag_key]}",
                )

        _get_scope_tags(self, "roleScopeTagIds")
        _get_scope_tags(self, "roleScopeTags")

        return data

    def get_scope_tags_id(self, data, scope_tags):
        """
        Get the ID of the scope tag.

        :param data: The data to search for the scope tag ID
        :param scope_tags: The scope tag to search for
        """

        def _get_scope_tags(self, scope_tag_key):
            self.log(
                function="get_scope_tags_id",
                msg="Checking if scope tags are in the data.",
            )
            # list comprehension to get the scope tag name
            if data.get(scope_tag_key):
                self.log(
                    function="get_scope_tags_id", msg="Scope tags are in the data."
                )
                data[scope_tag_key] = [
                    tag["id"]
                    for tag in scope_tags
                    if tag["displayName"] in data[scope_tag_key]
                ]
                self.log(
                    function="get_scope_tags_id",
                    msg=f"Scope tags: {data[scope_tag_key]}",
                )

        _get_scope_tags(self, "roleScopeTagIds")
        _get_scope_tags(self, "roleScopeTags")

        return data
