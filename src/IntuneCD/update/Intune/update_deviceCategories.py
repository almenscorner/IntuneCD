#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Device Categories in Intune.
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
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceCategories"


def update(path, token, report, remove, scope_tags):
    """
    This function updates all Device Categories in Intune if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_summary = []
    # Set Device Categories path
    configpath = path + "/" + "Device Categories"
    # If App Configuration path exists, continue
    if os.path.exists(configpath):
        # get all Device Categories
        mem_data = makeapirequest(ENDPOINT, token)
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

            category_value = {}

            # If Category exists, continue
            if mem_data["value"]:
                for val in mem_data["value"]:
                    if repo_data["displayName"] == val["displayName"]:
                        category_value = val
                        mem_data["value"].remove(val)

            if category_value:
                print("-" * 90)
                category_id = category_value["id"]
                category_value = remove_keys(category_value)

                diff = DeepDiff(category_value, repo_data, ignore_order=True).get(
                    "values_changed", {}
                )

                # If any changed values are found, push them to Intune
                if diff and report is False:
                    repo_data.pop("platform", None)
                    request_data = json.dumps(repo_data)
                    makeapirequestPatch(
                        ENDPOINT + "/" + category_id,
                        token,
                        q_param=None,
                        jdata=request_data,
                    )

                diff_config = DiffSummary(
                    data=diff,
                    name=repo_data["displayName"],
                    type="Device Category",
                )

                diff_summary.append(diff_config)

            # If Category does not exist, create it
            else:
                print("-" * 90)
                print(
                    "Device Category not found, creating category: "
                    + repo_data["displayName"]
                )
                if report is False:
                    request_json = json.dumps(repo_data)
                    post_request = makeapirequestPost(
                        ENDPOINT,
                        token,
                        q_param=None,
                        jdata=request_json,
                        status_code=201,
                    )
                    print("Device Category created with id: " + post_request["id"])

        # If any Device Categories are left in mem_data, remove them from Intune as they are not in the repo
        if mem_data.get("value", None) is not None and remove is True:
            for val in mem_data["value"]:
                print("-" * 90)
                print(
                    "Removing Device Configuration from Intune: " + val["displayName"]
                )
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}",
                        token,
                        status_code=200,
                    )

    return diff_summary
