#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all External Collaboration Settings in Entra.
"""

import glob
import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.check_file import check_file
from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.graph_request import makeapirequest, makeapirequestPatch
from ...intunecdlib.load_file import load_file

# Set MS Graph endpoint
BASE_ENDPOINT = "https://graph.microsoft.com/beta/policies/authorizationPolicy"


def update(path, token, report):
    """
    This function updates all External Collaboration Settings in Entra if the configuration in Entra differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_summary = []
    # Set External Collaboration Settings path
    configpath = path + "/Entra/Authorization Policy/" + "authorization_policy.*"

    file = glob.glob(configpath)
    # If authorization policy path exists, continue
    if file:
        # get all External Collaboration Settings
        entra_data = makeapirequest(BASE_ENDPOINT, token)

        file = check_file(
            configpath,
            os.path.join(
                path,
                "Entra",
                "Authorization Policy",
                file[0].split(os.sep)[-1],
            ),
        )
        if file is False:
            return diff_summary
        # Check which format the file is saved as then open file, load data
        # and set query parameter
        with open(file, encoding="utf-8") as f:
            repo_data = load_file(file, f)

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
                    BASE_ENDPOINT + "/authorizationPolicy",
                    token,
                    q_param=None,
                    jdata=request_data,
                    status_code=204,
                )

            diff_config = DiffSummary(
                data=diff,
                name="Authorization Policy",
                type="External Collaboration Settings",
            )

            diff_summary.append(diff_config)

    return diff_summary
