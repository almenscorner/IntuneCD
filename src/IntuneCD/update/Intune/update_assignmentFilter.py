#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Filters in Intune.
"""

import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.check_file import check_file
from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.graph_request import (
    makeapirequest,
    makeapirequestPatch,
    makeapirequestPost,
)
from ...intunecdlib.load_file import load_file
from ...intunecdlib.remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/assignmentFilters"


def update(path, token, report):
    """
    This function updates all Filters in Intune if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_summary = []
    # Set Filters path
    configpath = path + "/" + "Filters"
    # If App Configuration path exists, continue
    if os.path.exists(configpath):
        # get all filters
        mem_data = makeapirequest(ENDPOINT, token)

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            # Check which format the file is saved as then open file, load data
            # and set query parameter
            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)

            filter_value = {}

            # If Filter exists, continue
            if mem_data["value"]:
                for val in mem_data["value"]:
                    if repo_data["displayName"] == val["displayName"]:
                        filter_value = val

            if filter_value:
                print("-" * 90)
                filter_id = filter_value["id"]
                filter_value = remove_keys(filter_value)

                filter_value.pop("payloads", None)
                repo_data.pop("payloads", None)

                diff = DeepDiff(filter_value, repo_data, ignore_order=True).get(
                    "values_changed", {}
                )

                # If any changed values are found, push them to Intune
                if diff and report is False:
                    repo_data.pop("platform", None)
                    request_data = json.dumps(repo_data)
                    makeapirequestPatch(
                        ENDPOINT + "/" + filter_id,
                        token,
                        q_param=None,
                        jdata=request_data,
                    )

                diff_config = DiffSummary(
                    data=diff,
                    name=repo_data["displayName"],
                    type="Filter",
                )

                diff_summary.append(diff_config)

            # If Filter does not exist, create it
            else:
                print("-" * 90)
                print(
                    "Assignment filter not found, creating filter: "
                    + repo_data["displayName"]
                )
                if report is False:
                    repo_data.pop("payloads", None)
                    request_json = json.dumps(repo_data)
                    post_request = makeapirequestPost(
                        ENDPOINT,
                        token,
                        q_param=None,
                        jdata=request_json,
                        status_code=201,
                    )
                    print("Assignment filter created with id: " + post_request["id"])

    return diff_summary
