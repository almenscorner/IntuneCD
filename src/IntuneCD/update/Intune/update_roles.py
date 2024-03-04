#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Roles in Intune.
"""

import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.check_file import check_file
from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.graph_request import (
    makeapirequest,
    makeapirequestDelete,
    makeapirequestPatch,
    makeapirequestPost,
)
from ...intunecdlib.load_file import load_file
from ...intunecdlib.process_scope_tags import get_scope_tags_id
from ...intunecdlib.remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/roleDefinitions"


def update(path, token, report, remove=False, scope_tags=None):
    """
    This function updates all Roles in Intune if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_summary = []
    # Set Roles path
    configpath = path + "/" + "Roles"
    # If App Configuration path exists, continue
    if os.path.exists(configpath):
        # get all Roles
        q_param = {"$filter": "isBuiltIn eq false"}
        mem_data = makeapirequest(ENDPOINT, token, q_param)

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            # Check which format the file is saved as then open file, load data
            # and set query parameter
            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)

            if scope_tags:
                repo_data = get_scope_tags_id(repo_data, scope_tags)

            role_value = {}

            # If Filter exists, continue
            if mem_data["value"]:
                for val in mem_data["value"]:
                    if repo_data["displayName"] == val["displayName"]:
                        role_value = val
                        mem_data["value"].remove(val)

            if role_value:
                print("-" * 90)
                role_id = role_value["id"]
                role_value = remove_keys(role_value)

                repo_data.pop("roleAssignments", None)
                role_value.pop("permissions", None)
                role_value["rolePermissions"][0].pop("actions", None)

                diff = DeepDiff(
                    role_value,
                    repo_data,
                    ignore_order=True,
                    exclude_paths="root['rolePermissions']",
                ).get("values_changed", {})

                actions_diff = DeepDiff(
                    role_value["rolePermissions"][0]["resourceActions"],
                    repo_data["rolePermissions"][0]["resourceActions"],
                    ignore_order=True,
                )

                # If any changed values are found, push them to Intune
                if diff or actions_diff and report is False:
                    repo_data.pop("isBuiltInRoleDefinition", None)
                    repo_data.pop("isBuiltIn", None)
                    request_data = json.dumps(repo_data)
                    makeapirequestPatch(
                        ENDPOINT + "/" + role_id,
                        token,
                        q_param=None,
                        jdata=request_data,
                    )

                diff_config = DiffSummary(
                    data=diff,
                    name=repo_data["displayName"],
                    type="Role",
                )

                if actions_diff:
                    print("Resource Actions changed, check commit history for details")

                diff_summary.append(diff_config)

            # If Filter does not exist, create it
            else:
                print("-" * 90)
                print("Role not found, creating role: " + repo_data["displayName"])
                if report is False:
                    repo_data.pop("roleAssignments", None)
                    request_json = json.dumps(repo_data)
                    post_request = makeapirequestPost(
                        ENDPOINT,
                        token,
                        q_param=None,
                        jdata=request_json,
                    )
                    print("Role created with id: " + post_request["id"])

        # If any Roles are left in mem_data, remove them from Intune as they are not in the repo
        if mem_data.get("value", None) is not None and remove is True:
            for val in mem_data["value"]:
                print("-" * 90)
                print("Removing Role from Intune: " + val["displayName"])
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}", token, status_code=200
                    )

    return diff_summary
