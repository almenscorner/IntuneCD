#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all App Protection Policies in Intune.
"""

import re

from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import (
    batch_assignment,
    batch_request,
    get_object_assignment,
)
from ...intunecdlib.graph_request import makeapirequest, makeAuditRequest
from ...intunecdlib.process_audit_data import process_audit_data
from ...intunecdlib.process_scope_tags import get_scope_tags_name
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
q_param = {
    "$filter": "(microsoft.graph.managedApp/appAvailability) eq null or (microsoft.graph.managedApp/appAvailability) "
    "eq 'lineOfBusiness' or isAssigned eq true"
}
ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"


def match(platform, odata_input) -> bool:
    """
    This function matches the platform from the @odata.type.

    :param platform: The platform to match
    :param input: The OData type
    :return: False if no match, True if match
    """

    string = f".*{platform}.*$"
    pattern = re.compile(string)
    platform_match = pattern.match(odata_input, re.IGNORECASE)
    return bool(platform_match)


# Get all applications and save them in specified path
def savebackup(path, output, exclude, token, append_id, audit, scope_tags):
    """
    Saves all applications in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    audit_data = None
    data = makeapirequest(ENDPOINT, token, q_param)
    assignment_responses = batch_assignment(
        data, "deviceAppManagement/mobileApps/", "/assignments", token
    )
    app_ids = [app["id"] for app in data["value"]]
    scope_tag_responses = batch_request(
        app_ids, "deviceAppManagement/mobileApps/", "?$select=roleScopeTagIds,id", token
    )

    if audit:
        graph_filter = "componentName eq 'MobileApp'"
        audit_data = makeAuditRequest(graph_filter, token)

    for app in data["value"]:
        app_name = ""
        platform = ""
        results["config_count"] += 1

        scope_tag_data = [v for v in scope_tag_responses if app["id"] == v["id"]]
        if scope_tag_data:
            app["roleScopeTagIds"] = scope_tag_data[0]["roleScopeTagIds"]

        if scope_tags:
            app = get_scope_tags_name(app, scope_tags)

        if "assignments" not in exclude:
            assignments = get_object_assignment(app["id"], assignment_responses)
            if assignments:
                app["assignments"] = assignments

        # if audit:
        #    audit_data = get_audit_log(app["id"], audit_responses)

        graph_id = app["id"]
        app = remove_keys(app)
        app.pop("description", None)

        # If app type is VPP, add Apple ID to the name as the app can exist
        # multiple times
        if app["@odata.type"] == "#microsoft.graph.iosVppApp":
            app_name = (
                app["displayName"]
                + "_iOSVppApp_"
                + str(app["vppTokenAppleId"].split("@")[0])
            )
        elif app["@odata.type"] == "#microsoft.graph.macOsVppApp":
            app_name = (
                app["displayName"]
                + "_macOSVppApp_"
                + str(app["vppTokenAppleId"].split("@")[0])
            )
        # If app type is Win32 or MSI, add version to the name as multiple
        # versions can exist
        elif app["@odata.type"] == "#microsoft.graph.win32LobApp":
            if not app["displayVersion"]:
                app_name = app["displayName"] + "_Win32"
            else:
                app_name = (
                    app["displayName"]
                    + "_Win32_"
                    + str(app["displayVersion"]).replace(".", "_")
                )
        elif app["@odata.type"] == "#microsoft.graph.windowsMobileMSI":
            app_name = (
                app["displayName"]
                + "_WinMSI_"
                + str(app["productVersion"]).replace(".", "_")
            )
        # If app is not VPP, Win32 or MSI only add the app type to the name
        else:
            app_name = app["displayName"] + "_" + str(app["@odata.type"].split(".")[2])

        # Get application platform
        if match("ios", str(app["@odata.type"]).lower()) is True:
            platform = "iOS"
        if match("macos", str(app["@odata.type"]).lower()) is True:
            platform = "macOS"
        if match("android", str(app["@odata.type"]).lower()) is True:
            platform = "Android"
        if match("windows", str(app["@odata.type"]).lower()) is True:
            platform = "Windows"
        if match("microsoft", str(app["@odata.type"]).lower()) is True:
            platform = "Windows"
        if match("win32", str(app["@odata.type"]).lower()) is True:
            platform = "Windows"
        if match("office", str(app["@odata.type"]).lower()) is True:
            platform = "Office Suite"
        if app["@odata.type"] == "#microsoft.graph.webApp":
            platform = "Web App"

        if app.get("usedLicenseCount") and "VPPusedLicenseCount" in exclude:
            app.pop("usedLicenseCount", None)

        print(f"Backing up Application: {app['displayName']}")

        configpath = f"{path}/Applications/{platform}/"

        # Get filename without illegal characters
        fname = clean_filename(app_name)
        if append_id:
            fname = f"{fname}__{graph_id}"

        save_output(output, configpath, fname, app)

        results["outputs"].append(fname)

        if audit_data:
            compare_data = {"type": "resourceId", "value": graph_id}
            process_audit_data(
                audit_data, compare_data, path, f"{configpath}{fname}.{output}"
            )

    return results
