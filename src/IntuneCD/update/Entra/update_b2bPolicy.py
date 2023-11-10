#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all b2bpolicy Settings in Entra.
"""

import glob
import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.azure_request import make_azure_request, make_azure_request_post
from ...intunecdlib.check_file import check_file
from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.load_file import load_file

# Set MS Graph endpoint
ENDPOINT = "B2B/b2bPolicy"


def update(path, token, report):
    """
    This function updates all b2bpolicy Settings in Entra if the configuration in Entra differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_summary = []
    # Set b2bpolicy Settings path
    configpath = path + "/Entra/External Collaboration Settings/" + "b2b_policy.*"

    file = glob.glob(configpath)
    # If b2bpolicy path exists, continue
    if file:
        # get all b2bpolicy Settings
        entra_data = make_azure_request(token, ENDPOINT)

        file = check_file(
            configpath,
            os.path.join(
                path,
                "Entra",
                "External Collaboration Settings",
                file[0].split(os.sep)[-1],
            ),
        )
        if file is False:
            return diff_summary
        # Check which format the file is saved as then open file, load data
        # and set query parameter
        with open(file, encoding="utf-8") as f:
            repo_data = load_file(file, f)

        if entra_data:
            print("-" * 90)
            diff = DeepDiff(
                entra_data,
                repo_data,
                ignore_order=True,
            ).get("values_changed", {})

            # If any changed values are found, push them to Entra
            if diff and report is False:
                request_data = json.dumps(repo_data)
                make_azure_request_post(
                    token, ENDPOINT, data=request_data, q_param=None, status_code=200
                )

            diff_config = DiffSummary(
                data=diff,
                name="b2bpolicy",
                type="External Collaboration Settings",
            )

            diff_summary.append(diff_config)

    return diff_summary
