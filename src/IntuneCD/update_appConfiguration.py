#!/usr/bin/env python3

"""
This module is used to update all App Configuration Assignments in Intune.
"""

import json
import os

from deepdiff import DeepDiff
from .graph_request import makeapirequest, makeapirequestPatch, makeapirequestPost
from .graph_batch import batch_assignment, get_object_assignment
from .update_assignment import update_assignment, post_assignment_update
from .remove_keys import remove_keys
from .get_diff_output import get_diff_output
from .check_file import check_file
from .load_file import load_file

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileAppConfigurations"
APP_ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"


def update(path, token, assignment=False):
    """
    This function updates all App Configuration Polices in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_count = 0
    # Set App Configuration path
    configpath = path + "/" + "App Configuration/"
    # If App Configuration path exists, continue
    if os.path.exists(configpath):

        # Get App Configurations
        mem_data = makeapirequest(ENDPOINT, token)
        # Get current assignments
        mem_assignments = batch_assignment(
            mem_data,
            'deviceAppManagement/mobileAppConfigurations/',
            '/assignments',
            token)

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue

            # Check which format the file is saved as then open file, load data
            # and set query parameter
            with open(file) as f:
                repo_data = load_file(filename, f)
                # Create object to pass in to assignment function
                assign_obj = {}
                if "assignments" in repo_data:
                    assign_obj = repo_data['assignments']
                repo_data.pop('assignments', None)

                # If App Configuration exists, continue
                data = {'value': ''}
                if mem_data['value']:
                    for val in mem_data['value']:
                        if repo_data['@odata.type'] == val['@odata.type'] and \
                                repo_data['displayName'] == val['displayName']:
                            data['value'] = val

                if data['value']:
                    print("-" * 90)
                    mem_id = data['value']['id']
                    # Remove keys before using DeepDiff
                    data = remove_keys(data)
                    repo_data.pop('targetedMobileApps', None)

                    diff = DeepDiff(
                        data['value'], repo_data, ignore_order=True).get(
                        'values_changed', {})

                    # If any changed values are found, push them to Intune
                    if diff:
                        diff_count += 1
                        print("Updating App configuration: " +
                              repo_data['displayName'] + ", values changed:")
                        values = get_diff_output(diff)
                        for value in values:
                            print(value)
                        request_data = json.dumps(repo_data)
                        q_param = None
                        makeapirequestPatch(
                            ENDPOINT + "/" + mem_id,
                            token,
                            q_param,
                            request_data,
                            status_code=204)
                    else:
                        print(
                            'No difference found for App configuration: ' +
                            repo_data['displayName'])

                    if assignment:
                        mem_assign_obj = get_object_assignment(
                            mem_id, mem_assignments)
                        update = update_assignment(
                            assign_obj, mem_assign_obj, token)
                        if update is not None:
                            request_data = {}
                            request_data['assignments'] = update
                            post_assignment_update(
                                request_data,
                                mem_id,
                                'deviceAppManagement/mobileAppConfigurations/',
                                '/microsoft.graph.managedDeviceMobileAppConfiguration/assign',
                                token)

                # If App Configuration does not exist, create it and assign
                else:
                    print("-" * 90)
                    print("App Configuration not found, creating: " +
                          repo_data['displayName'])
                    app_ids = {}
                    # If backup contains targeted apps, search for the app
                    if repo_data['targetedMobileApps']:
                        q_param = {
                            "$filter": "(isof(" + "'" + str(
                                repo_data['targetedMobileApps']['type']).replace(
                                '#',
                                '') + "'" + '))',
                            "$search": repo_data['targetedMobileApps']['appName']}
                        app_request = makeapirequest(
                            APP_ENDPOINT, token, q_param)
                        if app_request['value']:
                            app_ids = app_request['value'][0]['id']
                    # If the app could be found and matches type and name in
                    # backup, continue to create
                    if app_ids:
                        repo_data.pop('targetedMobileApps')
                        repo_data['targetedMobileApps'] = [app_ids]
                        request_json = json.dumps(repo_data)
                        post_request = makeapirequestPost(
                            ENDPOINT, token, q_param=None, jdata=request_json, status_code=201)
                        mem_assign_obj = []
                        assignment = update_assignment(
                            assign_obj, mem_assign_obj, token)
                        if assignment is not None:
                            request_data = {}
                            request_data['assignments'] = assignment
                            post_assignment_update(
                                request_data,
                                post_request['id'],
                                'deviceAppManagement/mobileAppConfigurations/',
                                '/microsoft.graph.managedDeviceMobileAppConfiguration/assign',
                                token)
                        print("App Configuration created with id: " +
                              post_request['id'])
                    else:
                        print(
                            "App configured in App Configuration profile could not be found, skipping creation")

    return diff_count
