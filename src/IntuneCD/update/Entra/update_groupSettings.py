#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Group Settings in Entra.
"""

import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.check_file import check_file
from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.graph_request import makeapirequest, makeapirequestPatch
from ...intunecdlib.load_file import load_file

# Set MS Graph endpoint
BASE_ENDPOINT = "https://graph.microsoft.com/v1.0/groupSettings"


def update(path, token, report):
    """
    This function updates all Group Settings in Entra if the configuration in Entra differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_summary = []
    # Set Group Settings path
    configpath = path + "/Entra/Group Settings/"
    if os.path.exists(configpath):
        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)

            entra_data = makeapirequest(BASE_ENDPOINT, token)

            if entra_data and entra_data.get("value"):
                for entra_value in entra_data["value"]:
                    if repo_data["templateId"] == entra_value["templateId"]:
                        print("-" * 90)
                        diff = DeepDiff(
                            entra_value["values"],
                            repo_data["values"],
                            ignore_order=True,
                        ).get("values_changed", {})

                        # If any changed values are found, push them to Entra
                        if diff and report is False:
                            request_data = json.dumps(repo_data)
                            makeapirequestPatch(
                                BASE_ENDPOINT + "/" + entra_value["id"],
                                token,
                                q_param=None,
                                jdata=request_data,
                                status_code=204,
                            )

                        diff_config = DiffSummary(
                            data=diff,
                            name=repo_data["displayName"],
                            type="Group Settings",
                        )

                        diff_summary.append(diff_config)

    return diff_summary
