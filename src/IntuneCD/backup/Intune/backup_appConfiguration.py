#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all App Configuration Polices in Intune.
"""

import base64
import json

from ...intunecdlib.check_prefix import check_prefix_match
from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import batch_assignment, get_object_assignment
from ...intunecdlib.graph_request import makeapirequest, makeAuditRequest
from ...intunecdlib.process_audit_data import process_audit_data
from ...intunecdlib.process_scope_tags import get_scope_tags_name
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = (
    "https://graph.microsoft.com/beta/deviceAppManagement/mobileAppConfigurations"
)
APP_ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"


# Get all App Configuration policies and save them in specified path
def savebackup(path, output, exclude, token, prefix, append_id, audit, scope_tags):
    """
    Saves all App Configuration policies in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    audit_data = None
    configpath = path + "/" + "App Configuration/"
    data = makeapirequest(ENDPOINT, token)
    if audit:
        graph_filter = "componentName eq 'MobileAppConfiguration'"
        audit_data = makeAuditRequest(graph_filter, token)

    if data["value"]:
        assignment_responses = batch_assignment(
            data, "deviceAppManagement/mobileAppConfigurations/", "/assignments", token
        )

        for profile in data["value"]:
            if prefix and not check_prefix_match(profile["displayName"], prefix):
                continue

            results["config_count"] += 1

            if scope_tags:
                profile = get_scope_tags_name(profile, scope_tags)
            if "assignments" not in exclude:
                assignments = get_object_assignment(profile["id"], assignment_responses)
                if assignments:
                    profile["assignments"] = assignments

            graph_id = profile["id"]
            profile = remove_keys(profile)

            # Get name and type of app on App Configuration Profile
            app_dict = {}
            for app_id in profile["targetedMobileApps"]:
                app_data = makeapirequest(APP_ENDPOINT + "/" + app_id, token)
                if app_data:
                    app_dict["appName"] = app_data["displayName"]
                    app_dict["type"] = app_data["@odata.type"]

            if app_dict:
                profile.pop("targetedMobileApps")
                profile["targetedMobileApps"] = app_dict

            if profile.get("payloadJson"):
                try:
                    profile["payloadJson"] = base64.b64decode(
                        profile["payloadJson"]
                    ).decode("utf-8")
                    profile["payloadJson"] = json.loads(profile["payloadJson"])
                except (UnicodeDecodeError, json.decoder.JSONDecodeError):
                    print("Unable to decode payloadJson for " + profile["displayName"])

            print("Backing up App Configuration: " + profile["displayName"])

            # Get filename without illegal characters
            fname = clean_filename(
                f"{profile['displayName']}_{str(profile['@odata.type'].split('.')[2])}"
            )
            if append_id:
                fname = f"{fname}__{graph_id}"
            # Save App Configuration as JSON or YAML depending on configured value
            # in "-o"
            save_output(output, configpath, fname, profile)

            results["outputs"].append(fname)

            if audit_data:
                compare_data = {"type": "resourceId", "value": graph_id}
                process_audit_data(
                    audit_data, compare_data, path, f"{configpath}{fname}.{output}"
                )

    return results
