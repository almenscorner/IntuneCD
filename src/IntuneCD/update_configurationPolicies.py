#!/usr/bin/env python3

"""
This module is used to update all Settings Catalog assignments in Intune,
"""

import json
import os

from deepdiff import DeepDiff
from .graph_request import makeapirequest, makeapirequestPut, makeapirequestPost
from .graph_batch import batch_assignment, get_object_assignment
from .update_assignment import update_assignment, post_assignment_update
from .check_file import check_file
from .load_file import load_file
from .get_diff_output import get_diff_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/configurationPolicies"


def update(path, token, assignment=False):
    """
    This function updates all Settings Catalog configurations in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_count = 0
    # Set Settings Catalog path
    configpath = path + "/" + "Settings Catalog/"

    if os.path.exists(configpath):
        # Get configurations policies
        mem_data = makeapirequest(ENDPOINT, token)
        # Get current assignments
        mem_assignments = batch_assignment(
            mem_data,
            'deviceManagement/configurationPolicies/',
            '/assignments',
            token)

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            (name, ext) = os.path.splitext(filename)
            # Check which format the file is saved as then open file, load data
            # and set query parameter
            with open(file) as f:
                repo_data = load_file(filename, f)

                # Create object to pass in to assignment function
                assign_obj = {}
                if "assignments" in repo_data:
                    assign_obj = repo_data['assignments']
                repo_data.pop('assignments', None)

                data = {'value': ''}
                if mem_data['value']:
                    for val in mem_data['value']:
                        if repo_data['name'] == val['name']:
                            data['value'] = val

                # If Filter exists, continue
                if data['value']:
                    print("-" * 90)
                    # Get Filter data from Intune
                    mem_policy_data = makeapirequest(
                        ENDPOINT + "/" + data['value']['id'], token)
                    # Get Filter settings from Intune
                    mem_policy_settings = makeapirequest(
                        ENDPOINT + "/" + data['value']['id'] + "/settings", token)
                    # Add settings to the data dictionary
                    mem_policy_data['settings'] = mem_policy_settings['value']

                    diff = DeepDiff(
                        mem_policy_data,
                        repo_data,
                        ignore_order=True).get(
                        'values_changed',
                        {})

                    # If any changed values are found, push them to Intune
                    if diff:
                        diff_count += 1
                        print("Updating Settings Catalog policy: " +
                              name + ", values changed:")
                        values = get_diff_output(diff)
                        for value in values:
                            print(value)
                        request_data = json.dumps(repo_data)
                        q_param = None
                        makeapirequestPut(
                            ENDPOINT +
                            "/" +
                            data['value']['id'],
                            token,
                            q_param,
                            request_data,
                            status_code=204)
                    else:
                        print(
                            'No difference found for Settings Catalog policy: ' + name)

                    if assignment:
                        mem_assign_obj = get_object_assignment(
                            data['value']['id'], mem_assignments)
                        update = update_assignment(
                            assign_obj, mem_assign_obj, token)
                        if update is not None:
                            request_data = {'assignments': update}
                            post_assignment_update(
                                request_data,
                                data['value']['id'],
                                'deviceManagement/configurationPolicies',
                                'assign',
                                token)

                # If Configuration Policy does not exist, create it and assign
                else:
                    print("-" * 90)
                    print(
                        "Configuration Policy not found, creating Policy: " +
                        repo_data['name'])
                    repo_data.pop('settingCount', None)
                    request_json = json.dumps(repo_data)
                    post_request = makeapirequestPost(
                        ENDPOINT, token, q_param=None, jdata=request_json, status_code=201)
                    mem_assign_obj = []
                    assignment = update_assignment(
                        assign_obj, mem_assign_obj, token)
                    if assignment is not None:
                        request_data = {'assignments': assignment}
                        post_assignment_update(
                            request_data,
                            post_request['id'],
                            'deviceManagement/configurationPolicies',
                            'assign',
                            token)
                    print(
                        "Configuration Policy created with id: " +
                        post_request['id'])

    return diff_count
