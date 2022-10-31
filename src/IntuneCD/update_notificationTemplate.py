#!/usr/bin/env python3

"""
This module is used to update all Notification Templates in Intune.
"""

import json
import os

from deepdiff import DeepDiff
from .graph_request import makeapirequest, makeapirequestPatch, makeapirequestPost
from .check_file import check_file
from .load_file import load_file
from .remove_keys import remove_keys
from .get_diff_output import get_diff_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/notificationMessageTemplates"


def update(path, token):
    """
    This function updates all Notification Templates in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    """

    diff_count = 0
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
            with open(file) as f:
                repo_data = load_file(filename, f)

                data = {'value': ''}
                if mem_data['value']:
                    for val in mem_data['value']:
                        if repo_data['displayName'] == val['displayName']:
                            data['value'] = val

                # If Notification Template exists, continue
                if data['value']:
                    print("-" * 90)
                    # Get Notification Template data from Intune
                    q_param = "?$expand=localizedNotificationMessages"
                    mem_template_data = makeapirequest(
                        ENDPOINT + "/" + data['value']['id'], token, q_param)
                    # Create dict to compare Intune data with JSON/YAML data
                    repo_template_data = {
                        "displayName": repo_data['displayName'],
                        "brandingOptions": repo_data['brandingOptions'],
                        "roleScopeTagIds": repo_data['roleScopeTagIds']
                    }

                    diff = DeepDiff(
                        mem_template_data,
                        repo_template_data,
                        ignore_order=True).get(
                        'values_changed',
                        {})

                    # If any changed values are found, push them to Intune
                    if diff:
                        diff_count += 1
                        print(
                            "Updating Message Template: " +
                            mem_template_data['displayName'] +
                            ", values changed:")
                        values = get_diff_output(diff)
                        for value in values:
                            print(value)
                        request_data = json.dumps(repo_template_data)
                        q_param = None
                        makeapirequestPatch(
                            ENDPOINT +
                            "/" +
                            mem_template_data['id'],
                            token,
                            q_param,
                            request_data)
                    else:
                        print("No difference found for Message Template: " +
                              mem_template_data['displayName'])

                    # Check each configured locale on the Notification Template
                    # for changes
                    for mem_locale, repo_locale in zip(
                            mem_template_data['localizedNotificationMessages'],
                            repo_data['localizedNotificationMessages']):
                        del mem_locale['lastModifiedDateTime']
                        repo_locale = remove_keys(repo_locale)

                        diff = DeepDiff(
                            mem_locale, repo_locale, ignore_order=True).get(
                            'values_changed', {})

                        # If any changed values are found, push them to Intune
                        if diff:
                            diff_count += 1
                            print(
                                "Updating Message Template locale: " +
                                mem_locale['locale'] +
                                " for " +
                                mem_template_data['displayName'] +
                                ", values changed")
                            values = get_diff_output(diff)
                            for value in values:
                                print(value)
                            repo_locale.pop('isDefault', None)
                            repo_locale.pop('locale', None)
                            request_data = json.dumps(repo_locale)
                            q_param = None
                            makeapirequestPatch(
                                ENDPOINT +
                                "/" +
                                mem_template_data['id'] +
                                "/" +
                                "localizedNotificationMessages" +
                                "/" +
                                mem_locale['id'],
                                token,
                                q_param,
                                request_data)
                        else:
                            print(
                                "No difference in locale " +
                                mem_locale['locale'] +
                                " found for Message Template: " +
                                mem_template_data['displayName'])

                # If Notification Template does not exist, create it
                else:
                    print("-" * 90)
                    print(
                        "Notification template not found, creating template: " +
                        repo_data['displayName'])
                    template = {
                        "brandingOptions": repo_data['brandingOptions'],
                        "displayName": repo_data['displayName'],
                        "roleScopeTagIds": repo_data['roleScopeTagIds']
                    }
                    template_request_json = json.dumps(template)
                    template_post_request = makeapirequestPost(
                        ENDPOINT, token, q_param=None, jdata=template_request_json, status_code=200)
                    for locale in repo_data['localizedNotificationMessages']:
                        locale_request_json = json.dumps(locale)
                        makeapirequestPost(
                            ENDPOINT +
                            "/" +
                            template_post_request['id'] +
                            "/localizedNotificationMessages",
                            token,
                            q_param=None,
                            jdata=locale_request_json,
                            status_code=200)
                    print(
                        "Notification template created with id: " +
                        template_post_request['id'])

    return diff_count
