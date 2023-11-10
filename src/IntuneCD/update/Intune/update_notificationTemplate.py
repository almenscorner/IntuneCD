#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is used to update all Notification Templates in Intune.
"""

import json
import os

from deepdiff import DeepDiff

from ...intunecdlib.check_file import check_file
from ...intunecdlib.diff_summary import DiffSummary
from ...intunecdlib.graph_request import (
    makeapirequest,
    makeapirequestDelete,
    makeapirequestPatch,
    makeapirequestPost,
)
from ...intunecdlib.load_file import load_file
from ...intunecdlib.remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = (
    "https://graph.microsoft.com/beta/deviceManagement/notificationMessageTemplates"
)


def update(path, token, report, remove):
    """
    This function updates all Notification Templates in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_summary = []
    # Set Notification Template path
    configpath = path + "/" + "Compliance Policies/Message Templates/"
    # If Notification Template path exists, continue
    if os.path.exists(configpath):
        # Get notification templates
        mem_data = makeapirequest(ENDPOINT, token)

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            # Check which format the file is saved as then open file, load data
            # and set query parameter
            with open(file, encoding="utf-8") as f:
                repo_data = load_file(filename, f)

            data = {"value": ""}
            if mem_data["value"]:
                for val in mem_data["value"]:
                    if val["displayName"] == "EnrollmentNotificationInternalMEO":
                        continue
                    if repo_data["displayName"] == val["displayName"]:
                        data["value"] = val
                        mem_data["value"].remove(val)

            # If Notification Template exists, continue
            if data["value"]:
                print("-" * 90)
                # Get Notification Template data from Intune
                q_param = "?$expand=localizedNotificationMessages"
                mem_template_data = makeapirequest(
                    ENDPOINT + "/" + data.get("value").get("id"), token, q_param
                )
                # Create dict to compare Intune data with JSON/YAML data
                repo_template_data = {
                    "displayName": repo_data["displayName"],
                    "brandingOptions": repo_data["brandingOptions"],
                    "roleScopeTagIds": repo_data["roleScopeTagIds"],
                }

                diff = DeepDiff(
                    mem_template_data, repo_template_data, ignore_order=True
                ).get("values_changed", {})

                # If any changed values are found, push them to Intune
                if diff and report is False:
                    request_data = json.dumps(repo_template_data)
                    q_param = None
                    makeapirequestPatch(
                        ENDPOINT + "/" + mem_template_data["id"],
                        token,
                        q_param,
                        request_data,
                    )

                diff_config = DiffSummary(
                    data=diff,
                    name=repo_data["displayName"],
                    type="Notification Template",
                )

                # Check each configured locale on the Notification Template
                # for changes
                for mem_locale, repo_locale in zip(
                    mem_template_data["localizedNotificationMessages"],
                    repo_data["localizedNotificationMessages"],
                ):
                    del mem_locale["lastModifiedDateTime"]
                    repo_locale = remove_keys(repo_locale)

                    diff = DeepDiff(mem_locale, repo_locale, ignore_order=True).get(
                        "values_changed", {}
                    )

                    # If any changed values are found, push them to Intune
                    if diff and report is False:
                        repo_locale.pop("isDefault", None)
                        repo_locale.pop("locale", None)
                        request_data = json.dumps(repo_locale)
                        q_param = None
                        makeapirequestPatch(
                            ENDPOINT
                            + "/"
                            + mem_template_data["id"]
                            + "/"
                            + "localizedNotificationMessages"
                            + "/"
                            + mem_locale["id"],
                            token,
                            q_param,
                            request_data,
                        )

                    diff_locale = DiffSummary(
                        data=diff,
                        name=mem_locale["locale"],
                        type="Notification Template Locale",
                    )

                    diff_config.diffs += diff_locale.diffs
                    diff_config.count += diff_locale.count

                diff_summary.append(diff_config)

            # If Notification Template does not exist, create it
            else:
                print("-" * 90)
                print(
                    "Notification template not found, creating template: "
                    + repo_data["displayName"]
                )
                if report is False:
                    template = {
                        "brandingOptions": repo_data["brandingOptions"],
                        "displayName": repo_data["displayName"],
                        "roleScopeTagIds": repo_data["roleScopeTagIds"],
                    }
                    template_request_json = json.dumps(template)
                    template_post_request = makeapirequestPost(
                        ENDPOINT,
                        token,
                        q_param=None,
                        jdata=template_request_json,
                        status_code=200,
                    )
                    for locale in repo_data["localizedNotificationMessages"]:
                        locale_request_json = json.dumps(locale)
                        makeapirequestPost(
                            ENDPOINT
                            + "/"
                            + template_post_request["id"]
                            + "/localizedNotificationMessages",
                            token,
                            q_param=None,
                            jdata=locale_request_json,
                            status_code=200,
                        )
                    print(
                        "Notification template created with id: "
                        + template_post_request["id"]
                    )

        # If any Notification Template are left in mem_data, remove them from Intune as they are not in the repo
        if mem_data.get("value", None) is not None and remove is True:
            for val in mem_data["value"]:
                if val["displayName"] == "EnrollmentNotificationInternalMEO":
                    continue
                print("-" * 90)
                print(
                    "Removing Notification template from Intune: " + val["displayName"]
                )
                if report is False:
                    makeapirequestDelete(
                        f"{ENDPOINT}/{val['id']}", token, status_code=200
                    )

    return diff_summary
