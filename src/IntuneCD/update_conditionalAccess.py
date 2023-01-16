#!/usr/bin/env python3

"""
This module is used to update all Conditional Access Policy's in Intune.
"""

import json
import os

from deepdiff import DeepDiff
from .graph_request import makeapirequest, makeapirequestPatch, makeapirequestPost
from .check_file import check_file
from .load_file import load_file
from .remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/identity/conditionalAccess/policies"


def update(path, token, report):
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
            with open(file) as f:
                repo_data = load_file(filename, f)
                repo_data["conditions"].pop("users", None)

                data = {"value": ""}
                if mem_data["value"]:
                    for val in mem_data["value"]:
                        if repo_data["displayName"] == val["displayName"]:
                            data["value"] = val

                # If Conditional Access policy exists, continue
                if data["value"]:
                    if "id" not in data["value"]:
                        continue
                    print("-" * 90)

                    data["value"]["conditions"].pop("users", None)
                    if data["value"]["grantControls"]:
                        data["value"]["grantControls"].pop(
                            "authenticationStrength@odata.context", None
                        )

                    mem_id = data["value"]["id"]
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
                                if repo_data["grantControls"].get(
                                    "authenticationStrength"
                                ):
                                    id = (
                                        repo_data["grantControls"]
                                        .get("authenticationStrength", {})
                                        .get("id")
                                    )
                                    repo_data["grantControls"][
                                        "authenticationStrength"
                                    ] = ({"id": id} if id else None)
                                    repo_data["grantControls"]["operator"] = (
                                        "AND" if id else None
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
                                id = (
                                    repo_data["grantControls"]
                                    .get("authenticationStrength", {})
                                    .get("id")
                                )
                                repo_data["grantControls"]["authenticationStrength"] = (
                                    {"id": id} if id else None
                                )
                                repo_data["grantControls"]["operator"] = (
                                    "AND" if id else None
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

    return diff_count
