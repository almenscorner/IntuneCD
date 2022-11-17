#!/usr/bin/env python3

"""
This module is used to update all Windows Enrollment Status Page Profiles in Intune.
"""

import json
import os

from deepdiff import DeepDiff
from .graph_request import makeapirequest, makeapirequestPatch, makeapirequestPost
from .graph_batch import batch_assignment, get_object_assignment
from .update_assignment import update_assignment, post_assignment_update
from .check_file import check_file
from .load_file import load_file
from .remove_keys import remove_keys
from .get_diff_output import get_diff_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceEnrollmentConfigurations"
APP_ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"


def update(path, token, assignment=False):
    """
    This function updates all Windows Enrollment Status Page Profiles in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_count = 0
    # Set Windows Enrollment Status Page Profile path
    configpath = path + "/" + "Enrollment Profiles/Windows/ESP/"
    # If Windows Enrollment Profile path exists, continue
    if os.path.exists(configpath):
        # Get enrollment profiles
        mem_data = makeapirequest(ENDPOINT, token)
        # Get current assignment
        mem_assignments = batch_assignment(
            mem_data,
            'deviceManagement/deviceEnrollmentConfigurations/',
            '/assignments',
            token)

        for filename in os.listdir(configpath):
            file = check_file(configpath, filename)
            if file is False:
                continue
            # Check which format the file is saved as then open file, load data and set query parameter
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
                        if repo_data['displayName'] == val['displayName'] and repo_data['@odata.type'] == val['@odata.type']:
                            data['value'] = val

                # If Enrollment Status Page Profile exists, continue
                if data['value']:
                    print("-" * 90)
                    mem_id = data['value']['id']
                    # Remove keys before using DeepDiff
                    mem_data['value'][0] = remove_keys(mem_data['value'][0])

                    # Get application ID of configured apps
                    if 'selectedMobileAppNames' in repo_data:
                        app_ids = []
                        
                        for app in repo_data['selectedMobileAppNames']:
                            q_param = {
                            "$filter": f"(isof('{str(app['type']).replace('#','')}'))", 
                            "$search": '"' + app['name'] + '"'}

                            app_request = makeapirequest(
                                APP_ENDPOINT, token, q_param)
                            if app_request['value']:
                                app_ids.append(app_request['value'][0]['id'])

                        if app_ids:
                            repo_data.pop('selectedMobileAppNames', None)
                            repo_data['selectedMobileAppIds'] = app_ids
                        else:
                            print("No app found with name: " + app['name'])

                    diff = DeepDiff(
                        data['value'],
                        repo_data,
                        ignore_order=True).get(
                        'values_changed',
                        {})

                    # If any changed values are found, push them to Intune
                    if diff:
                        diff_count += 1
                        print("Updating Enrollment Status Page profile: " +
                              repo_data['displayName'] + ", values changed:")
                        values = get_diff_output(diff)
                        for value in values:
                            print(value)

                        repo_data.pop('priority', None)

                        request_data = json.dumps(repo_data)
                        q_param = None
                        makeapirequestPatch(
                            f"{ENDPOINT}/{mem_id}", token, q_param, request_data)
                    else:
                        print(
                            'No difference found for Enrollment Status Page profile: ' +
                            repo_data['displayName'])

                    if assignment:
                        mem_assign_obj = get_object_assignment(
                            mem_id, mem_assignments)
                        update = update_assignment(
                            assign_obj, mem_assign_obj, token)
                        if update is not None:
                            request_data = {'target': update}
                            post_assignment_update(
                                request_data,
                                mem_id,
                                'deviceManagement/deviceEnrollmentConfigurations',
                                'assign',
                                token,
                                status_code=201)

                # If Enrollmen Status Page profile does not exist, create it and assign
                else:
                    print("-" * 90)
                    print(
                        "Enrollment Status Page profile not found, creating profile: " +
                        repo_data['displayName'])
                    request_json = json.dumps(repo_data)
                    post_request = makeapirequestPost(
                        ENDPOINT, token, q_param=None, jdata=request_json, status_code=201)
                    mem_assign_obj = []
                    assignment = update_assignment(
                        assign_obj, mem_assign_obj, token)
                    if assignment is not None:
                        assignments = []
                        for assign in assignment:
                            assignments.append({'target': assign['target']})
                        request_data = {'enrollmentConfigurationAssignments': assignments}

                        post_assignment_update(
                            request_data,
                            post_request['id'],
                            'deviceManagement/deviceEnrollmentConfigurations',
                            'assign',
                            token,
                            status_code=200)
                    print(
                        "Enrollment Status Page profile created with id: " +
                        post_request['id'])

    return diff_count
