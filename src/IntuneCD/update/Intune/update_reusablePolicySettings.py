#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Compliance Scripts in Intune.
"""

import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.check_file import check_file
from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.graph_request import (
    makeapirequest,
    makeapirequestDelete,
    makeapirequestPost,
    makeapirequestPut,
)
from ...intunecdlib.load_file import load_file
from ...intunecdlib.remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/reusablePolicySettings/"


def update(
    path,
    token,
    report=False,
    remove=False,
):
    """
    This function updates all Compliance scripts in Intune if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_summary = []
    # Set Compliance script path
    configpath = path + "/" + "Compliance Policies/Scripts/"
    # If Compliance script path exists, continue
    if os.path.exists(configpath):
        # Get scripts
        mem_ComplianceScript = makeapirequest(ENDPOINT, token)
        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            # Check which format the file is saved as then open file, load data
            # and set query parameter
            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)

            if not repo_data.get("settingDefinitionId"):
                continue

            data = {"value": ""}
            if mem_ComplianceScript["value"]:
                for val in mem_ComplianceScript["value"]:
                    if repo_data["displayName"] == val["displayName"]:
                        data["value"] = val
                        mem_ComplianceScript["value"].remove(val)

            # If Compliance script exists, continue
            if data["value"]:
                print("-" * 90)
                q_param = None
                # Get Compliance script details
                q_param = {
                    "$select": "id,settinginstance,displayname,description,settingDefinitionId,version"
                }
                mem_data = makeapirequest(
                    ENDPOINT + "/" + data.get("value").get("id"), token, q_param
                )
                mem_id = mem_data["id"]
                # Remove keys before using DeepDiff
                mem_data = remove_keys(mem_data)

                pdiff = DeepDiff(
                    mem_data["settingInstance"]["simpleSettingValue"]["value"],
                    repo_data["settingInstance"]["simpleSettingValue"]["value"],
                    ignore_order=True,
                ).get("values_changed", {})

                cdiff = DeepDiff(
                    mem_data,
                    repo_data,
                    ignore_order=True,
                    exclude_paths="root['settingInstance']['simpleSettingValue']['value']",
                ).get("values_changed", {})

                # If any changed values are found, push them to Intune
                if pdiff or cdiff and report is False:
                    request_data = json.dumps(repo_data)
                    q_param = None
                    makeapirequestPut(
                        ENDPOINT + "/" + mem_id,
                        token,
                        q_param,
                        request_data,
                        status_code=204,
                    )

                diff_config = DiffSummary(
                    data=cdiff,
                    name=repo_data["displayName"],
                    type="Compliance Script",
                )

                diff_script = DiffSummary(
                    data=pdiff,
                    name="",
                    type="Compliance Script",
                    message="Script changed, check commit history for details",
                    notify=False,
                )

                diff_config.diffs += diff_script.diffs
                diff_config.count += diff_script.count

                diff_summary.append(diff_config)

            # If Compliance script does not exist, create it and assign
            else:
                print("-" * 90)
                print(
                    "Compliance script not found, creating compliance script: "
                    + repo_data["displayName"]
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

                    print("Compliance script created with id: " + post_request["id"])

        # If any Compliance Scripts are left in mem_ComplianceScript, remove them from Intune as they are not in the repo
        if mem_ComplianceScript.get("value", None) is not None and remove is True:
            for val in mem_ComplianceScript["value"]:
                print("-" * 90)
                print("Removing Compliance Script from Intune: " + val["displayName"])
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}", token, status_code=200
                    )

    return diff_summary
