#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Group Settings in Entra.
"""
import glob
import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.azure_request import make_azure_request, make_azure_request_put
from ...intunecdlib.check_file import check_file
from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.load_file import load_file

# Set MS Graph endpoint
ENDPOINT = "RoamingSettings"


def update(path, token, report):
    """
    This function updates all Group Settings in Entra if the configuration in Entra differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_summary = []
    # Set Group Settings path
    configpath = path + "/Entra/Roaming Settings/" + "roaming_settings.*"

    file = glob.glob(configpath)
    # If roaming settings path exists, continue
    if file:
        # get all Group Settings
        entra_data = make_azure_request(token, ENDPOINT, "?ESRV2=true")

        file = check_file(
            configpath,
            os.path.join(path, "Entra", "Roaming Settings", file[0].split(os.sep)[-1]),
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
                make_azure_request_put(
                    token, ENDPOINT, data=request_data, q_param="?ESRV2=true"
                )

            diff_config = DiffSummary(
                data=diff,
                name="",
                type="Roaming Settings",
            )

            diff_summary.append(diff_config)

    return diff_summary
