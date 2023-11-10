#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Intents in Intune.
"""

from ...intunecdlib.check_prefix import check_prefix_match
from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import (
    batch_assignment,
    batch_intents,
    get_object_assignment,
)
from ...intunecdlib.graph_request import makeapirequest
from ...intunecdlib.save_output import save_output

# Set MS Graph base endpoint
BASE_ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement"
TEMPLATE_ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/templates"


# Get all Intents and save them in specified path
def savebackup(path, output, exclude, token, prefix, append_id):
    """
    Saves all Intents in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    configpath = path + "/" + "Management Intents/"
    intents = makeapirequest(BASE_ENDPOINT + "/intents", token)
    templates = makeapirequest(TEMPLATE_ENDPOINT, token)

    assignment_responses = batch_assignment(
        intents, "deviceManagement/intents/", "/assignments", token
    )
    intent_responses = batch_intents(intents, token)

    if intent_responses:
        for intent_value in intent_responses["value"]:
            if prefix and not check_prefix_match(intent_value["displayName"], prefix):
                continue

            results["config_count"] += 1
            print("Backing up Intent: " + intent_value["displayName"])

            for template in templates["value"]:
                if intent_value["templateId"] == template["id"]:
                    template_type = template["displayName"]

            configpath = path + "/" + "Management Intents/" + template_type + "/"

            if "assignments" not in exclude:
                assignments = get_object_assignment(
                    intent_value["id"], assignment_responses
                )
                if assignments:
                    intent_value["assignments"] = assignments

            for setting in intent_value["settingsDelta"]:
                setting.pop("id", None)
            graph_id = intent_value["id"]
            intent_value.pop("id", None)

            # Get filename without illegal characters
            fname = clean_filename(intent_value["displayName"])
            if append_id:
                fname = f"{fname}__{graph_id}"
            # Save Intent as JSON or YAML depending on configured value in "-o"
            save_output(output, configpath, fname, intent_value)

            results["outputs"].append(fname)

    return results
