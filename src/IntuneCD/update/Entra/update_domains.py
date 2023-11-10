#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Domains in Entra.
"""

import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.check_file import check_file
from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.graph_request import makeapirequest, makeapirequestPatch
from ...intunecdlib.load_file import load_file

# Set MS Graph endpoint
BASE_ENDPOINT = "https://graph.microsoft.com/beta/domains"


def update(path, token, report):
    """
    This function updates all Domains in Entra if the configuration in Entra differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_summary = []
    # Set Domains path
    configpath = path + "/Entra/Domains/"
    if os.path.exists(configpath):
        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)

            entra_data = makeapirequest(
                BASE_ENDPOINT, token, q_param=f"?$filter=id eq '{repo_data['id']}'"
            )

            if entra_data and entra_data.get("value"):
                print("-" * 90)
                diff = DeepDiff(
                    entra_data["value"][0],
                    repo_data,
                    ignore_order=True,
                ).get("values_changed", {})

                # If any changed values are found, push them to Entra
                if diff and report is False:
                    request_data = json.dumps(repo_data)
                    makeapirequestPatch(
                        BASE_ENDPOINT + "/" + repo_data["id"],
                        token,
                        q_param=None,
                        jdata=request_data,
                        status_code=204,
                    )

                diff_config = DiffSummary(
                    data=diff,
                    name=repo_data["id"],
                    type="Domains",
                )

                diff_summary.append(diff_config)

    return diff_summary
