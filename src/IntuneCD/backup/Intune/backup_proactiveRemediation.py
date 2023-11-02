#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Proactive Remediation in Intune.
"""

import base64
import os

from ...intunecdlib.check_prefix import check_prefix_match
from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import (
    batch_assignment,
    batch_request,
    get_object_assignment,
)
from ...intunecdlib.graph_request import makeapirequest
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceHealthScripts"


# Get all Proactive Remediation and save them in specified path
def savebackup(path, output, exclude, token, prefix, append_id):
    """
    Saves all Proactive Remediation in Intune to a JSON or YAML file and script files.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    configpath = f"{path}/Proactive Remediations/"
    data = makeapirequest(ENDPOINT, token)
    if data["value"]:
        pr_ids = []
        for script in data["value"]:
            pr_ids.append(script["id"])

        assignment_responses = batch_assignment(
            data, "deviceManagement/deviceHealthScripts/", "/assignments", token
        )
        pr_data_responses = batch_request(
            pr_ids, "deviceManagement/deviceHealthScripts/", "", token
        )

        for pr_details in pr_data_responses:
            if prefix and not check_prefix_match(pr_details["displayName"], prefix):
                continue

            if "Microsoft" not in pr_details["publisher"]:
                results["config_count"] += 1
                if "assignments" not in exclude:
                    assignments = get_object_assignment(
                        pr_details["id"], assignment_responses
                    )
                    if assignments:
                        pr_details["assignments"] = assignments

                graph_id = pr_details["id"]
                pr_details = remove_keys(pr_details)

                print(f"Backing up Proactive Remediation: {pr_details['displayName']}")

                # Get filename without illegal characters
                fname = clean_filename(pr_details["displayName"])
                if append_id:
                    fname = f"{fname}__{graph_id}"

                # Save Proactive Remediation as JSON or YAML depending on
                # configured value in "-o"
                save_output(output, configpath, fname, pr_details)

                results["outputs"].append(fname)

                if not os.path.exists(f"{configpath}/Script Data"):
                    os.makedirs(f"{configpath}/Script Data")

                # Save detection script to the Script Data folder
                results["config_count"] += 1
                fname = clean_filename(pr_details["displayName"])
                if append_id:
                    fname_id = f"__{graph_id}"
                else:
                    fname_id = ""
                decoded = base64.b64decode(pr_details["detectionScriptContent"]).decode(
                    "utf-8"
                )
                f = open(
                    f"{configpath}/Script Data/{fname}_DetectionScript{fname_id}.ps1",
                    "w",
                    encoding="utf-8",
                )
                f.write(decoded)
                # Save remediation script to the Script Data folder
                results["config_count"] += 1
                decoded = base64.b64decode(
                    pr_details["remediationScriptContent"]
                ).decode("utf-8")
                f = open(
                    f"{configpath}/Script Data/{fname}_RemediationScript{fname_id}.ps1",
                    "w",
                    encoding="utf-8",
                )
                f.write(decoded)

    return results
