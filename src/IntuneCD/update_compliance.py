#!/usr/bin/env python3

"""
This module is used to update all Compliance Policies in Intune.
"""

import json
import os

from deepdiff import DeepDiff
from .graph_request import makeapirequest, makeapirequestPatch, makeapirequestPost
from .graph_batch import batch_assignment, get_object_assignment
from .update_assignment import update_assignment, post_assignment_update
from .remove_keys import remove_keys
from .load_file import load_file
from .check_file import check_file
from .get_diff_output import get_diff_output


# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceCompliancePolicies"


def update(path, token, assignment=False):
    """
    This function updates all Compliance Polices in Intune,
    if the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_count = 0
    # Set Compliance Policy path
    configpath = path + "/" + "Compliance Policies/Policies/"
    # If App Configuration path exists, continue
    if os.path.exists(configpath):
        # Get compliance policies
        q_param = {
            "expand": "scheduledActionsForRule($expand=scheduledActionConfigurations)"}
        mem_data = makeapirequest(ENDPOINT, token, q_param)
        # Get current assignments
        mem_assignments = batch_assignment(
            mem_data,
            'deviceManagement/deviceCompliancePolicies/',
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

                # If Compliance Policy exists, continue
                data = {'value': ''}
                if mem_data['value']:
                    for val in mem_data['value']:
                        if repo_data['@odata.type'] == val['@odata.type'] and \
                                repo_data['displayName'] == val['displayName']:
                            data['value'] = val

                if data['value']:
                    print("-" * 90)
                    mem_id = data['value']['id']
                    data['value'] = remove_keys(data['value'])

                    if data['value']['scheduledActionsForRule']:
                        for rule in data['value']['scheduledActionsForRule']:
                            remove_keys(rule)
                        for scheduled_config in data['value']['scheduledActionsForRule'][0][
                                'scheduledActionConfigurations']:
                            remove_keys(scheduled_config)

                    diff = DeepDiff(
                        data['value'],
                        repo_data,
                        ignore_order=True,
                        exclude_paths="root['scheduledActionsForRule'][0]['scheduledActionConfigurations']").get(
                        'values_changed',
                        {})

                    # If any changed values are found, push them to Intune
                    if diff:
                        diff_count += 1
                        print("Updating Compliance policy: " +
                              repo_data['displayName'] + ", values changed:")
                        values = get_diff_output(diff)
                        for value in values:
                            print(value)

                        scheduled_actions = repo_data['scheduledActionsForRule']
                        repo_data.pop('scheduledActionsForRule', None)
                        request_data = json.dumps(repo_data)
                        q_param = None
                        makeapirequestPatch(
                            ENDPOINT + "/" + mem_id,
                            token,
                            q_param,
                            request_data,
                            status_code=204)
                        repo_data['scheduledActionsForRule'] = scheduled_actions

                    else:
                        print(
                            'No difference found for Compliance policy: ' +
                            repo_data['displayName'])

                    if repo_data['scheduledActionsForRule']:
                        for mem_rule, repo_rule in zip(
                                data['value']['scheduledActionsForRule'], repo_data['scheduledActionsForRule']):
                            rdiff = DeepDiff(
                                mem_rule, repo_rule, ignore_order=True).get(
                                'values_changed', {})
                        if rdiff:
                            diff_count += 1
                            print(
                                "Updating rules for Compliance Policy: " +
                                repo_data['displayName'] +
                                ", values changed:")
                            values = get_diff_output(rdiff)
                            for value in values:
                                print(value)
                            request_data = {
                                "deviceComplianceScheduledActionForRules": [
                                    {
                                        "ruleName": "PasswordRequired",
                                        "scheduledActionConfigurations":
                                            repo_data['scheduledActionsForRule'][0]['scheduledActionConfigurations']
                                    }
                                ]
                            }
                            request_json = json.dumps(request_data)
                            q_param = None
                            makeapirequestPost(
                                ENDPOINT +
                                "/" +
                                mem_id +
                                "/scheduleActionsForRules",
                                token,
                                q_param,
                                request_json)
                        else:
                            print(
                                'No difference in rules found for Compliance policy: ' +
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
                                'deviceManagement/deviceCompliancePolicies',
                                'assign',
                                token)

                # If Compliance Policy does not exist, create it and assign
                else:
                    print("-" * 90)
                    print(
                        "Compliance Policy not found, creating Policy: " +
                        repo_data['displayName'])
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
                            'deviceManagement/deviceCompliancePolicies',
                            'assign',
                            token)
                    print(
                        "Compliance Policy created with id: " +
                        post_request['id'])

    return diff_count
