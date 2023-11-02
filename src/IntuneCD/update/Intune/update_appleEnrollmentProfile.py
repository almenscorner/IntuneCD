#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Apple Enrollment profiles in Intune.
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
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/depOnboardingSettings/"


def update(path, token, report):
    """
    This function updates all Apple Enrollment Profiles in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_summary = []
    # Set Apple Enrollment Profile path
    configpath = path + "/" + "Enrollment Profiles/Apple/"
    # If Apple Enrollment Profile path exists, continue
    if os.path.exists(configpath):
        # Get IDs of all Apple Enrollment Profiles and add them to a list
        ids = []
        mem_data_accounts = makeapirequest(ENDPOINT, token)
        for a_id in mem_data_accounts["value"]:
            ids.append(a_id["id"])

        for profile in ids:
            for filename in os.listdir(configpath):
                file = check_file(configpath, filename)
                if file is False:
                    continue
                # Check which format the file is saved as then open file, load
                # data and set query parameter
                with open(file, encoding="utf-8") as f:
                    repo_data = load_file(filename, f)

                q_param = {
                    "$filter": "displayName eq " + "'" + repo_data["displayName"] + "'"
                }

                # Get Apple Enrollment Profile with query parameter
                profile_data = makeapirequest(
                    ENDPOINT + profile + "/enrollmentProfiles", token, q_param
                )

                # If Apple Enrollment Profile exists, continue
                if profile_data["value"]:
                    print("-" * 90)
                    pid = profile_data["value"][0]["id"]
                    # Remove keys before using DeepDiff
                    profile_data["value"][0] = remove_keys(profile_data["value"][0])

                    diff = DeepDiff(
                        profile_data["value"][0], repo_data, ignore_order=True
                    ).get("values_changed", {})

                    # If any changed values are found, push them to Intune
                    if diff and report is False:
                        request_data = json.dumps(repo_data)
                        q_param = None
                        makeapirequestPatch(
                            ENDPOINT + profile + "/enrollmentProfiles/" + pid,
                            token,
                            q_param,
                            request_data,
                            status_code=204,
                        )

                    diff_profile = DiffSummary(
                        data=diff,
                        name=repo_data["displayName"],
                        type="Apple Enrollment Profile",
                    )

                    diff_summary.append(diff_profile)

    return diff_summary
