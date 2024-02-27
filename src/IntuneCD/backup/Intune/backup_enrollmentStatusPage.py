#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Windows Enrollment Status Page profiles.
"""

from ...intunecdlib.check_prefix import check_prefix_match
from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_batch import batch_assignment, get_object_assignment
from ...intunecdlib.graph_request import makeapirequest
from ...intunecdlib.process_scope_tags import get_scope_tags_name
from ...intunecdlib.remove_keys import remove_keys
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = (
    "https://graph.microsoft.com/beta/deviceManagement/deviceEnrollmentConfigurations"
)
APP_ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"


# Get all Windows Enrollment Status Page profiles and save them in specified path
def savebackup(path, output, exclude, token, prefix, append_id, scope_tags):
    """
    Saves all Windows Enrollment Status Page profiles in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    configpath = path + "/" + "Enrollment Profiles/Windows/ESP/"
    data = makeapirequest(ENDPOINT, token)

    assignment_responses = batch_assignment(
        data, "deviceManagement/deviceEnrollmentConfigurations/", "/assignments", token
    )

    for profile in data["value"]:
        if prefix and not check_prefix_match(profile["displayName"], prefix):
            continue

        if (
            profile["@odata.type"]
            == "#microsoft.graph.windows10EnrollmentCompletionPageConfiguration"
        ):
            results["config_count"] += 1

            if scope_tags:
                profile = get_scope_tags_name(profile, scope_tags)
            if "assignments" not in exclude:
                assignments = get_object_assignment(profile["id"], assignment_responses)
                if assignments:
                    profile["assignments"] = assignments

            graph_id = profile["id"]
            profile = remove_keys(profile)

            # If the profile contains apps, get the name of the app
            if "selectedMobileAppIds" in profile:
                app_ids = profile["selectedMobileAppIds"]
                app_names = []
                for app_id in app_ids:
                    app_data = makeapirequest(APP_ENDPOINT + "/" + app_id, token)
                    if app_data:
                        app = {
                            "name": app_data["displayName"],
                            "type": app_data["@odata.type"],
                        }
                        app_names.append(app)
                if app_names:
                    profile.pop("selectedMobileAppIds", None)
                    profile["selectedMobileAppNames"] = app_names

            print("Backing up Enrollment Status Page: " + profile["displayName"])

            # Get filename without illegal characters
            fname = clean_filename(profile["displayName"])
            if append_id:
                fname = f"{fname}__{graph_id}"
            # Save Windows Enrollment Profile as JSON or YAML depending on
            # configured value in "-o"
            save_output(output, configpath, fname, profile)

            results["outputs"].append(fname)

    return results
