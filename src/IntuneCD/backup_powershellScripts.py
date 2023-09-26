#!/usr/bin/env python3

"""
This module backs up all Powershell scripts in Intune.
"""

import os
import base64

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .graph_batch import batch_assignment, get_object_assignment, batch_request
from .save_output import save_output
from .remove_keys import remove_keys
from .check_prefix import check_prefix_match

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceManagementScripts/"


# Get all Powershell scripts and save them in specified path
def savebackup(path, output, exclude, token, prefix):
    """
    Saves all Powershell scripts in Intune to a JSON or YAML file and script files.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    configpath = path + "/" + "Scripts/Powershell/"
    data = makeapirequest(ENDPOINT, token)
    if data["value"]:
        script_ids = []
        for script in data["value"]:
            script_ids.append(script["id"])

        assignment_responses = batch_assignment(
            data, "deviceManagement/deviceManagementScripts/", "/assignments", token
        )
        script_data_responses = batch_request(
            script_ids, "deviceManagement/deviceManagementScripts/", "", token
        )

        for script_data in script_data_responses:
            if prefix and not check_prefix_match(script_data["displayName"], prefix):
                continue

            results["config_count"] += 1
            if "assignments" not in exclude:
                assignments = get_object_assignment(
                    script_data["id"], assignment_responses
                )
                if assignments:
                    script_data["assignments"] = assignments

            script_data = remove_keys(script_data)

            print("Backing up Powershell script: " + script_data["displayName"])

            # Get filename without illegal characters
            fname = clean_filename(script_data["displayName"])
            # Save Powershell script as JSON or YAML depending on configured value
            # in "-o"
            save_output(output, configpath, fname, script_data)

            results["outputs"].append(fname)

            # Save Powershell script data to the script data folder
            if script_data.get("scriptContent"):
                if not os.path.exists(configpath + "Script Data/"):
                    os.makedirs(configpath + "Script Data/")
                decoded = base64.b64decode(script_data["scriptContent"]).decode("utf-8")
                f = open(configpath + "Script Data/" + script_data["fileName"], "w")
                f.write(decoded)

    return results
