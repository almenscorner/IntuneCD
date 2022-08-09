#!/usr/bin/env python3

"""
This module is used to update all App Protection Policies in Intune.
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
ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/"


def update(path, token, assignment=False):
    """
    This function updates all App Protection Polices in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_count = 0
    # Set App Protection path
    configpath = path + "/" + "App Protection/"
    # If App Configuration path exists, continue
    if os.path.exists(configpath):

        # Get App Protections
        mem_data = makeapirequest(f'{ENDPOINT}managedAppPolicies', token)
        # Get current assignments
        mem_assignments = batch_assignment(
            mem_data,
            'deviceAppManagement/',
            '/assignments',
            token,
            app_protection=True)

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            # Check which format the file is saved as then open file, load data
            # and set query parameter
            with open(file) as f:
                repo_data = load_file(filename, f)

                if repo_data:
                    if repo_data['@odata.type'] == "#microsoft.graph.mdmWindowsInformationProtectionPolicy":
                        platform = "mdmWindowsInformationProtectionPolicies"
                    elif repo_data['@odata.type'] == "#microsoft.graph.windowsInformationProtectionPolicy":
                        platform = "windowsInformationProtectionPolicies"
                    else:
                        platform = f"{str(repo_data['@odata.type']).split('.')[2]}s"

                # Create object to pass in to assignment function
                assign_obj = {}
                if "assignments" in repo_data:
                    assign_obj = repo_data['assignments']
                repo_data.pop('assignments', None)

                # If App Protection exists, continue
                data = {'value': ''}
                if mem_data['value']:
                    for val in mem_data['value']:
                        if 'targetedAppManagementLevels' in val and 'targetedAppManagementLevels' in repo_data:
                            if repo_data['targetedAppManagementLevels'] == val['targetedAppManagementLevels'] and \
                                    repo_data['displayName'] == val['displayName']:
                                data['value'] = val
                        elif repo_data['@odata.type'] == val['@odata.type'] and \
                                repo_data['displayName'] == val['displayName']:
                            data['value'] = val

                if data['value']:
                    print("-" * 90)
                    mem_id = data['value']['id']
                    # Remove keys before using DeepDiff
                    data['value'] = remove_keys(data['value'])

                    diff = DeepDiff(
                        data['value'],
                        repo_data,
                        ignore_order=True).get(
                        'values_changed',
                        {})

                    # If any changed values are found, push them to Intune
                    if diff:
                        diff_count += 1
                        print(
                            "Updating App protection: " +
                            repo_data['displayName'] +
                            ", values changed:")
                        values = get_diff_output(diff)
                        for value in values:
                            print(value)
                        request_data = json.dumps(repo_data)
                        q_param = None
                        makeapirequestPatch(
                            f'{ENDPOINT}{platform}/{mem_id}',
                            token,
                            q_param,
                            request_data,
                            status_code=204)
                    else:
                        print(
                            'No difference found for App protection: ' +
                            repo_data['displayName'])

                    if assignment:
                        mem_assign_obj = get_object_assignment(
                            mem_id, mem_assignments)
                        update = update_assignment(
                            assign_obj, mem_assign_obj, token)
                        if update is not None:
                            request_data = {'assignments': update}
                            post_assignment_update(
                                request_data,
                                mem_id,
                                f'deviceAppManagement/{platform}',
                                'assign',
                                token,
                                status_code=204)

                # If App Protection does not exist, create it and assign
                else:
                    print("-" * 90)
                    print("App Protection not found, creating policy: " +
                          repo_data['displayName'])
                    request_json = json.dumps(repo_data)
                    post_request = makeapirequestPost(
                        f'{ENDPOINT}managedAppPolicies',
                        token,
                        q_param=None,
                        jdata=request_json,
                        status_code=201)
                    mem_assign_obj = []
                    assignment = update_assignment(
                        assign_obj, mem_assign_obj, token)
                    if assignment is not None:
                        request_data = {'assignments': assignment}
                        post_assignment_update(
                            request_data,
                            post_request['id'],
                            f'deviceAppManagement/{platform}',
                            'assign',
                            token,
                            status_code=204)
                    print(
                        "App Protection created with id: " +
                        post_request['id'])

    return diff_count
