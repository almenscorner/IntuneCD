#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Conditional Access Policy's in Intune.
"""

import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.check_file import check_file
from ...intunecdlib.graph_request import (
    makeapirequest,
    makeapirequestDelete,
    makeapirequestPatch,
    makeapirequestPost,
)
from ...intunecdlib.load_file import load_file
from ...intunecdlib.remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/identity/conditionalAccess/policies"


def update(path, token, report, remove):
    """
    This function updates all Conditional Access Profiles in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_count = 0
    # Set Conditional Access Profile path
    configpath = path + "/" + "Conditional Access/"
    # If Conditional Access Profile path exists, continue
    if os.path.exists(configpath):
        # Get CA profiles
        mem_data = makeapirequest(ENDPOINT, token)

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            # Check which format the file is saved as then open file, load data
            # and set query parameter
            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)
                repo_data["conditions"].pop("users", None)

            data = {"value": ""}
            if mem_data["value"]:
                for val in mem_data["value"]:
                    if repo_data["displayName"] == val["displayName"]:
                        data["value"] = val
                        mem_data["value"].remove(val)

            # If Conditional Access policy exists, continue
            if data["value"]:
                if "id" not in data["value"]:
                    continue
                print("-" * 90)

                data.get("value").get("conditions").pop("users", None)
                if data.get("value").get("grantControls"):
                    data.get("value").get("grantControls").pop(
                        "authenticationStrength@odata.context", None
                    )

                mem_id = data.get("value").get("id")
                # Remove keys before using DeepDiff
                data["value"] = remove_keys(data["value"])

                diff = DeepDiff(data["value"], repo_data, ignore_order=True)

                # If any changed values are found, push them to Intune
                if diff:
                    diff_count += 1
                    print(
                        "Updating Conditional Access policy: "
                        + repo_data["displayName"]
                    )

                    if report is False:
                        # If authenticationStrength is set, set operator to AND and remove unnecessary keys
                        if repo_data.get("grantControls"):
                            if repo_data["grantControls"].get("authenticationStrength"):
                                g_id = (
                                    repo_data["grantControls"]
                                    .get("authenticationStrength", {})
                                    .get("id")
                                )
                                repo_data["grantControls"]["authenticationStrength"] = (
                                    {"id": g_id} if g_id else None
                                )
                                repo_data["grantControls"]["operator"] = (
                                    "AND" if g_id else None
                                )

                        request_data = json.dumps(repo_data)
                        q_param = None
                        makeapirequestPatch(
                            f"{ENDPOINT}/{mem_id}",
                            token,
                            q_param,
                            request_data,
                            status_code=204,
                        )
                else:
                    print(
                        "No changes found for Conditional Access policy: "
                        + repo_data["displayName"]
                    )

            # If Conditional Access policy does not exist, create it and assign
            else:
                print("-" * 90)
                print(
                    "Conditional Access policy not found, creating policy: "
                    + repo_data["displayName"]
                )
                if report is False:
                    # Users is a required key, set to None as updating assignment is currently not supported
                    repo_data["conditions"]["users"] = {"includeUsers": ["None"]}
                    # If authenticationStrength is set, set operator to AND and remove unnecessary keys
                    if repo_data.get("grantControls"):
                        if repo_data["grantControls"].get("authenticationStrength"):
                            g_id = (
                                repo_data["grantControls"]
                                .get("authenticationStrength", {})
                                .get("id")
                            )
                            repo_data["grantControls"]["authenticationStrength"] = (
                                {"id": g_id} if g_id else None
                            )
                            repo_data["grantControls"]["operator"] = (
                                "AND" if g_id else None
                            )

                    request_json = json.dumps(repo_data)
                    post_request = makeapirequestPost(
                        ENDPOINT,
                        token,
                        q_param=None,
                        jdata=request_json,
                        status_code=201,
                    )

                    if post_request:
                        print(
                            "Conditional Access policy created with id: "
                            + post_request["id"]
                        )

        # If any Conditional Access policy are left in mem_data, remove them from Intune as they are not in the repo
        if mem_data.get("value", None) is not None and remove is True:
            for val in mem_data["value"]:
                print("-" * 90)
                print(
                    "Removing Conditional Access Policy from Intune: "
                    + val["displayName"]
                )
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}", token, status_code=204
                    )

    return diff_count
