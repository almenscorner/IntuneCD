#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Endpoint Security configurations (intents) in Intune,
"""

import glob
import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.graph_batch import (
    batch_assignment,
    batch_intents,
    get_object_assignment,
)
from ...intunecdlib.graph_request import (
    makeapirequest,
    makeapirequestDelete,
    makeapirequestPost,
)
from ...intunecdlib.load_file import load_file
from .update_assignment import post_assignment_update, update_assignment

# Set MS Graph base endpoint
BASE_ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement"


def update(
    path, token, assignment=False, report=False, create_groups=False, remove=False
):
    """
    This function updates all Endpoint Security configurations (intents) in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_summary = []
    # Set Intent path
    configpath = path + "/" + "Management Intents/"
    # If Intents path exists, continue
    if os.path.exists(configpath):
        # Get intents
        intents = makeapirequest(BASE_ENDPOINT + "/intents", token)
        intent_responses = batch_intents(intents, token)
        # Get current assignment
        mem_assignments = batch_assignment(
            intents, "deviceManagement/intents/", "/assignments", token
        )

        # Set glob pattern
        pattern = configpath + "*/*"
        for filename in glob.glob(pattern, recursive=True):
            # If file is .DS_Store, skip
            if filename == ".DS_Store":
                continue
            # If file is .md, skip
            if filename.endswith(".md"):
                continue

            # Check which format the file is saved as then open file, load data
            # and set query parameter
            with open(filename, encoding="utf-8") as f:
                repo_data = load_file(filename, f)

            # Create object to pass in to assignment function
            assign_obj = {}
            if "assignments" in repo_data:
                assign_obj = repo_data["assignments"]
            repo_data.pop("assignments", None)

            mem_data = {}
            for intent in intent_responses["value"]:
                if (
                    repo_data["displayName"] == intent["displayName"]
                    and repo_data["templateId"] == intent["templateId"]
                ):
                    mem_data = intent
                    intent_responses["value"].remove(intent)

            if repo_data.get("templateId") == "e44c2ca3-2f9a-400a-a113-6cc88efd773d":
                print("Endpoint detection and response is currently not supported...")
                continue

            # If Intent exists, continue
            if mem_data:
                print("-" * 90)
                print(
                    "Checking if Intent: "
                    + repo_data["displayName"]
                    + " has any updates"
                )

                # Compare category settings from Intune with JSON/YAML
                for repo_setting in repo_data["settingsDelta"]:
                    for mem_setting in mem_data["settingsDelta"]:
                        if "id" in mem_setting:
                            mem_setting_id = mem_setting["id"]
                            mem_setting.pop("id", None)
                        if repo_setting["definitionId"] == mem_setting["definitionId"]:
                            diff = DeepDiff(
                                mem_setting, repo_setting, ignore_order=True
                            ).get("values_changed", {})

                    # If any changed values are found, push them to Intune
                    if diff and report is False:
                        # Create dict that we will use as the request json
                        if "value" not in repo_setting:
                            intent_type = "valueJson"
                            value = repo_setting["valueJson"]
                        else:
                            intent_type = "value"
                            value = repo_setting["value"]
                        settings = {
                            "settings": [
                                {
                                    "id": mem_setting_id,
                                    "definitionId": repo_setting["definitionId"],
                                    "@odata.type": repo_setting["@odata.type"],
                                    intent_type: value,
                                }
                            ]
                        }
                        request_data = json.dumps(settings)
                        q_param = None
                        makeapirequestPost(
                            BASE_ENDPOINT
                            + "/intents/"
                            + mem_data["id"]
                            + "/updateSettings",
                            token,
                            q_param,
                            request_data,
                            status_code=204,
                        )

                    diff_intent = DiffSummary(
                        data=diff,
                        name=repo_setting["definitionId"].split("_")[1],
                        type="Intent",
                        notify=False,
                    )

                    diff_summary.append(diff_intent)

                if assignment:
                    mem_assign_obj = get_object_assignment(
                        mem_data["id"], mem_assignments
                    )
                    assignment_update = update_assignment(
                        assign_obj, mem_assign_obj, token, create_groups
                    )
                    if assignment_update is not None:
                        request_data = {"assignments": assignment_update}
                        post_assignment_update(
                            request_data,
                            mem_data["id"],
                            "deviceManagement/intents",
                            "assign",
                            token,
                            status_code=204,
                        )

            # If Intent does not exist, create it and assign
            else:
                print("-" * 90)
                print("Intent not found, creating Intent: " + repo_data["displayName"])
                if report is False:
                    template_id = repo_data["templateId"]
                    repo_data.pop("templateId")
                    request_json = json.dumps(repo_data)
                    post_request = makeapirequestPost(
                        BASE_ENDPOINT + "/templates/" + template_id + "/createInstance",
                        token,
                        q_param=None,
                        jdata=request_json,
                    )
                    mem_assign_obj = []
                    assignment = update_assignment(
                        assign_obj, mem_assign_obj, token, create_groups
                    )
                    if assignment is not None:
                        request_data = {"assignments": assignment}
                        post_assignment_update(
                            request_data,
                            post_request["id"],
                            "deviceManagement/intents",
                            "assign",
                            token,
                            status_code=204,
                        )
                    print("Intent created with id: " + post_request["id"])

        # If any Intents are left in intent_responses, remove them from Intune as they are not in the repo
        if intent_responses.get("value", None) is not None and remove is True:
            for val in intent_responses["value"]:
                print("-" * 90)
                print("Removing Management Intent from Intune: " + val["displayName"])
                if report is False:
                    makeapirequestDelete(
                        f"{BASE_ENDPOINT}/intents/{val['id']}", token, status_code=200
                    )

    return diff_summary
