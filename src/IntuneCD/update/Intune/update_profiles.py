#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unsupported-assignment-operation

"""
This module is used to update all Device Configuration Profiles in Intune.
"""

import base64
import json
import os
import plistlib

from deepdiff import DeepDiff

from ...intunecdlib.check_file import check_file
from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.graph_batch import batch_assignment, get_object_assignment
from ...intunecdlib.graph_request import (
    makeapirequest,
    makeapirequestDelete,
    makeapirequestPatch,
    makeapirequestPost,
)
from ...intunecdlib.load_file import load_file
from ...intunecdlib.remove_keys import remove_keys
from .update_assignment import post_assignment_update, update_assignment

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceConfigurations"


def update(
    path, token, assignment=False, report=False, create_groups=False, remove=False
):
    """
    This function updates all Device Configurations in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_summary = []
    # Set Device Configurations path
    configpath = path + "/" + "Device Configurations/"
    # If Device Configurations path exists, continue
    if os.path.exists(configpath):
        # Get profiles
        mem_data = makeapirequest(ENDPOINT, token)
        # Get current assignment
        mem_assignments = batch_assignment(
            mem_data, "deviceManagement/deviceConfigurations/", "/assignments", token
        )

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)

            # Create object to pass in to assignment function
            assign_obj = {}
            if "assignments" in repo_data:
                assign_obj = repo_data["assignments"]
            repo_data.pop("assignments", None)

            # If Device Configuration exists, continue
            data = {"value": ""}
            if mem_data["value"]:
                for val in mem_data["value"]:
                    if (
                        repo_data["@odata.type"] == val["@odata.type"]
                        and repo_data["displayName"] == val["displayName"]
                    ):
                        data["value"] = val
                        mem_data["value"].remove(val)

            if data["value"]:
                print("-" * 90)
                mem_id = data.get("value").get("id")
                # Remove keys before using DeepDiff
                data["value"] = remove_keys(data["value"])

                # If Device Configuration is custom macOS or iOS, compare
                # the .mobileconfig
                if (
                    repo_data["@odata.type"]
                    == "#microsoft.graph.macOSCustomConfiguration"
                ) or (
                    repo_data["@odata.type"]
                    == "#microsoft.graph.iosCustomConfiguration"
                ):
                    if os.path.exists(
                        configpath + "mobileconfig/" + repo_data["payloadFileName"]
                    ):
                        with open(
                            configpath + "mobileconfig/" + repo_data["payloadFileName"],
                            "rb",
                        ) as f:
                            repo_payload_config = plistlib.load(f)

                        decoded = base64.b64decode(
                            data.get("value").get("payload")
                        ).decode("utf-8")
                        f = open(
                            configpath + "temp.mobileconfig", "w", encoding="utf-8"
                        )
                        f.write(decoded)
                        with open(configpath + "temp.mobileconfig", "rb") as f:
                            mem_payload_config = plistlib.load(f)

                        pdiff = DeepDiff(
                            mem_payload_config,
                            repo_payload_config,
                            ignore_order=True,
                        ).get("values_changed", {})
                        cdiff = DeepDiff(
                            data["value"],
                            repo_data,
                            ignore_order=True,
                            exclude_paths="root['payload']",
                        ).get("values_changed", {})

                        # If any changed values are found, push them to
                        # Intune
                        if pdiff or cdiff:
                            if report is False:
                                payload = plistlib.dumps(repo_payload_config)
                                repo_data["payload"] = str(
                                    base64.b64encode(payload), "utf-8"
                                )
                                request_data = json.dumps(repo_data)
                                q_param = None
                                makeapirequestPatch(
                                    ENDPOINT + "/" + mem_id,
                                    token,
                                    q_param,
                                    request_data,
                                    status_code=204,
                                )

                        diff_profile = DiffSummary(
                            data=cdiff,
                            name=repo_data["displayName"],
                            type="Configuration Profile",
                        )

                        diff_config = DiffSummary(
                            data=pdiff,
                            name=repo_data["payloadName"],
                            type="Mobileconfig",
                        )

                        diff_profile.diffs += diff_config.diffs
                        diff_profile.count += diff_config.count
                        diff_summary.append(diff_profile)

                        os.remove(configpath + "temp.mobileconfig")

                    else:
                        print(
                            "No mobileconfig found for profile: "
                            + repo_data["displayName"]
                        )

                # If Device Configuration is custom Win10, compare the OMA
                # settings
                elif (
                    data.get("value").get("@odata.type")
                    == "#microsoft.graph.windows10CustomConfiguration"
                ):
                    print(
                        "Checking if Win10 Custom Profile: "
                        + repo_data["displayName"]
                        + " has any updates"
                    )
                    omas = []
                    for setting in data.get("value").get("omaSettings"):
                        if setting["isEncrypted"]:
                            decoded_oma = {}
                            oma_value = makeapirequest(
                                ENDPOINT
                                + "/"
                                + mem_id
                                + "/getOmaSettingPlainTextValue(secretReferenceValueId='"
                                + setting["secretReferenceValueId"]
                                + "')",
                                token,
                            )
                            decoded_oma["@odata.type"] = setting["@odata.type"]
                            decoded_oma["displayName"] = setting["displayName"]
                            decoded_oma["description"] = setting["description"]
                            decoded_oma["omaUri"] = setting["omaUri"]
                            decoded_oma["value"] = oma_value
                            decoded_oma["isEncrypted"] = True
                            decoded_oma["secretReferenceValueId"] = None
                            omas.append(decoded_oma)
                        elif not setting["isEncrypted"]:
                            omas.append(setting)

                    data["value"].pop("omaSettings")
                    data["value"]["omaSettings"] = omas

                    repo_omas = []
                    for mem_omaSetting, repo_omaSetting in zip(
                        data.get("value").get("omaSettings"),
                        repo_data["omaSettings"],
                    ):
                        diff = DeepDiff(
                            mem_omaSetting,
                            repo_omaSetting,
                            ignore_order=True,
                            exclude_paths="root['isEncrypted']",
                        ).get("values_changed", {})

                        # If any changed values are found, push them to
                        # Intune
                        if diff:
                            if isinstance(repo_omaSetting["value"], dict):
                                repo_omaSetting = remove_keys(repo_omaSetting)
                                repo_omaSetting["value"] = repo_omaSetting["value"][
                                    "value"
                                ]
                                repo_omas.append(repo_omaSetting)
                            else:
                                repo_omaSetting = remove_keys(repo_omaSetting)
                                repo_omas.append(repo_omaSetting)

                        diff_oma = DiffSummary(
                            data=diff,
                            name=repo_omaSetting["omaUri"],
                            type="OMA Setting",
                        )

                        diff_summary.append(diff_oma)

                    repo_data.pop("omaSettings")
                    repo_data["omaSettings"] = repo_omas

                    if repo_omas and report is False:
                        request_data = json.dumps(repo_data)
                        q_param = None
                        makeapirequestPatch(
                            ENDPOINT + "/" + mem_id,
                            token,
                            q_param,
                            request_data,
                            status_code=204,
                        )

                # Updating Windows update rings is currently not supported
                elif (
                    data.get("value").get("@odata.type")
                    == "#microsoft.graph.windowsUpdateForBusinessConfiguration"
                ):
                    continue

                # If Device Configuration is not custom, compare the values
                else:
                    diff = DeepDiff(data["value"], repo_data, ignore_order=True).get(
                        "values_changed", {}
                    )

                    # If any changed values are found, push them to Intune
                    if diff and report is False:
                        request_data = json.dumps(repo_data)
                        q_param = None
                        makeapirequestPatch(
                            ENDPOINT + "/" + mem_id,
                            token,
                            q_param,
                            request_data,
                            status_code=204,
                        )

                    diff_profile = DiffSummary(
                        data=diff,
                        name=repo_data["displayName"],
                        type="Configuration Profile",
                    )

                    diff_summary.append(diff_profile)

                if assignment:
                    mem_assign_obj = get_object_assignment(mem_id, mem_assignments)
                    assignment_update = update_assignment(
                        assign_obj, mem_assign_obj, token, create_groups
                    )
                    if assignment_update is not None:
                        request_data = {"assignments": assignment_update}
                        post_assignment_update(
                            request_data,
                            mem_id,
                            "deviceManagement/deviceConfigurations",
                            "assign",
                            token,
                        )

            # If profile does not exist, create it and assign
            else:
                # If profile is custom win10, create correct omaSettings
                # format before posting
                if (
                    repo_data["@odata.type"]
                    == "#microsoft.graph.windows10CustomConfiguration"
                ):
                    repo_omas = []
                    for repo_omaSetting in repo_data["omaSettings"]:
                        if isinstance(repo_omaSetting["value"], dict):
                            repo_omaSetting = remove_keys(repo_omaSetting)
                            repo_omaSetting["value"] = repo_omaSetting["value"]["value"]
                            repo_omas.append(repo_omaSetting)
                        else:
                            repo_omaSetting = remove_keys(repo_omaSetting)
                            repo_omas.append(repo_omaSetting)
                    repo_data.pop("omaSettings")
                    repo_data["omaSettings"] = repo_omas
                # Post new profile
                print("-" * 90)
                print(
                    "Profile not found, creating profile: " + repo_data["displayName"]
                )
                if report is False:
                    request_json = json.dumps(repo_data)
                    post_request = makeapirequestPost(
                        ENDPOINT,
                        token,
                        q_param=None,
                        jdata=request_json,
                        status_code=201,
                    )
                    print("Profile created with id: " + post_request["id"])

                    mem_assign_obj = []
                    assignment = update_assignment(
                        assign_obj, mem_assign_obj, token, create_groups
                    )
                    if assignment is not None:
                        request_data = {"assignments": assignment}
                        post_assignment_update(
                            request_data,
                            post_request["id"],
                            "deviceManagement/deviceConfigurations",
                            "assign",
                            token,
                        )

        # If any Profiles are left in mem_data, remove them from Intune as they are not in the repo
        if mem_data.get("value", None) is not None and remove is True:
            for val in mem_data["value"]:
                print("-" * 90)
                print("Removing Profile from Intune: " + val["displayName"])
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}", token, status_code=200
                    )

    return diff_summary
