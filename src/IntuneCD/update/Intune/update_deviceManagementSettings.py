#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Device Management Settings in Intune.
"""

import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.check_file import check_file
from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.graph_request import makeapirequest, makeapirequestPatch
from ...intunecdlib.load_file import load_file
from ...intunecdlib.remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/"


def update(path, token, report):
    """
    This function updates all Device Management Settings in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_summary = []
    # Set Settings path
    configpath = path + "/" + "Device Management Settings/"
    # If Device Management Settings path exists, continue
    if os.path.exists(configpath):
        mem_data = makeapirequest(f"{ENDPOINT}/settings", token)

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            # Check which format the file is saved as then open file, load
            # data and set query parameter
            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)
            q_param = None

            # If Device Mangement Settigns exists, continue
            if mem_data:
                print("-" * 90)
                # Remove keys before using DeepDiff
                mem_data = remove_keys(mem_data)

                diff = DeepDiff(mem_data, repo_data, ignore_order=True).get(
                    "values_changed", {}
                )

                # If any changed values are found, push them to Intune
                if diff and report is False:
                    json_data = {"settings": repo_data}
                    request_data = json.dumps(json_data)
                    q_param = None
                    makeapirequestPatch(
                        ENDPOINT,
                        token,
                        q_param,
                        request_data,
                        status_code=204,
                    )

                diff_settings = DiffSummary(
                    data=diff,
                    name="",
                    type="Device Management Settings",
                )

                diff_summary.append(diff_settings)

    return diff_summary
