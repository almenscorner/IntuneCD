#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Authentication Methods in Entra.
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
BASE_ENDPOINT = "https://graph.microsoft.com/beta/policies/authenticationMethodsPolicy"


def update(path, token, report):
    """
    This function updates all Authentication Methods in Entra if the configuration in Entra differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_summary = []
    # Set Authentication Methods path
    configpath = path + "/Entra/Authentication Methods/" + "authentication_methods.*"

    file = glob.glob(configpath)
    # If authentication methods path exists, continue
    if file:
        # get all Authentication Methods
        entra_data = makeapirequest(BASE_ENDPOINT, token)

        file = check_file(
            configpath,
            os.path.join(
                path, "Entra", "Authentication Methods", file[0].split(os.sep)[-1]
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
            entra_data.pop("authenticationMethodConfigurations", None)
            entra_data.pop("policyMigrationState", None)
            repo_data.pop("authenticationMethodConfigurations", None)
            repo_data.pop("policyMigrationState", None)

            diff = DeepDiff(
                entra_data,
                repo_data,
                ignore_order=True,
            ).get("values_changed", {})

            # If any changed values are found, push them to Entra
            if diff and report is False:
                request_data = json.dumps(repo_data)
                makeapirequestPatch(
                    BASE_ENDPOINT,
                    token,
                    q_param=None,
                    jdata=request_data,
                    status_code=204,
                )

            diff_config = DiffSummary(
                data=diff,
                name="",
                type="Authentication Methods Policy",
            )

            diff_summary.append(diff_config)

    return diff_summary
