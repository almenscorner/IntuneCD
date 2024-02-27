#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up Device Configurations in Intune.
"""

import base64
import os

from ...intunecdlib.check_prefix import check_prefix_match
from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import batch_assignment, get_object_assignment
from ...intunecdlib.graph_request import makeapirequest, makeAuditRequest
from ...intunecdlib.process_audit_data import process_audit_data
from ...intunecdlib.process_scope_tags import get_scope_tags_name
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceConfigurations"


# Get all Device Configurations and save them in specified path
def savebackup(
    path,
    output,
    exclude,
    token,
    prefix,
    append_id,
    ignore_omasettings,
    audit,
    scope_tags,
):
    """
    Saves all Device Configurations in Intune to a JSON or YAML file and custom macOS/iOS to .mobileconfig.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    audit_data = None
    configpath = path + "/" + "Device Configurations/"
    data = makeapirequest(ENDPOINT, token)

    assignment_responses = batch_assignment(
        data, "deviceManagement/deviceConfigurations/", "/assignments", token
    )
    if audit:
        graph_filter = "componentName eq 'DeviceConfiguration'"
        audit_data = makeAuditRequest(graph_filter, token)

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
        pid = profile["id"]
        profile = remove_keys(profile)

        print("Backing up profile: " + profile["displayName"])

        # Get filename without illegal characters
        fname = clean_filename(
            f"{profile['displayName']}_{str(profile['@odata.type']).split('.')[2]}"
        )
        if append_id:
            fname = f"{fname}__{graph_id}"

        # If profile is custom macOS or iOS, decode the payload
        if (profile["@odata.type"] == "#microsoft.graph.macOSCustomConfiguration") or (
            profile["@odata.type"] == "#microsoft.graph.iosCustomConfiguration"
        ):
            decoded = base64.b64decode(profile["payload"]).decode("utf-8")

            if not os.path.exists(configpath + "/" + "mobileconfig/"):
                os.makedirs(configpath + "/" + "mobileconfig/")
            # Save decoded payload as .mobileconfig
            results["config_count"] += 1
            f = open(
                configpath + "/" + "mobileconfig/" + profile["payloadFileName"],
                "w",
                encoding="utf-8",
            )
            f.write(decoded)
            # Save Device Configuration as JSON or YAML depending on configured
            # value in "-o"
            save_output(output, configpath, fname, profile)

            results["outputs"].append(fname)

            if audit_data:
                compare_data = {"type": "resourceId", "value": graph_id}
                process_audit_data(
                    audit_data, compare_data, path, f"{configpath}{fname}.{output}"
                )

        # If Device Configuration is custom Win10 and the OMA settings are
        # encrypted, get them in plain text
        elif profile[
            "@odata.type"
        ] == "#microsoft.graph.windows10CustomConfiguration" and profile.get(
            "omaSettings"
        ):
            if not ignore_omasettings:
                omas = []
                for setting in profile["omaSettings"]:
                    if setting.get("isEncrypted"):
                        decoded_oma = {}
                        decoded_oma["@odata.type"] = setting["@odata.type"]
                        decoded_oma["displayName"] = setting["displayName"]
                        decoded_oma["description"] = setting["description"]
                        decoded_oma["omaUri"] = setting["omaUri"]
                        decoded_oma["isEncrypted"] = False
                        decoded_oma["secretReferenceValueId"] = None
                        oma_value = makeapirequest(
                            ENDPOINT
                            + "/"
                            + pid
                            + "/getOmaSettingPlainTextValue(secretReferenceValueId='"
                            + setting["secretReferenceValueId"]
                            + "')",
                            token,
                        )
                        decoded_oma["value"] = oma_value
                        omas.append(decoded_oma)
                    else:
                        omas.append(setting)

            else:
                omas = profile["omaSettings"]

            profile["omaSettings"] = omas

            # Save Device Configuration as JSON or YAML depending on configured
            # value in "-o"
            save_output(output, configpath, fname, profile)

            results["outputs"].append(fname)

            if audit_data:
                compare_data = {"type": "resourceId", "value": graph_id}
                process_audit_data(
                    audit_data, compare_data, path, f"{configpath}{fname}.{output}"
                )

        # If Device Configuration are not custom, save it as JSON or YAML
        # depending on configured value in "-o"
        else:
            save_output(output, configpath, fname, profile)

            results["outputs"].append(fname)

            if audit_data:
                compare_data = {"type": "resourceId", "value": graph_id}
                process_audit_data(
                    audit_data, compare_data, path, f"{configpath}{fname}.{output}"
                )

    return results
