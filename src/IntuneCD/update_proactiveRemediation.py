#!/usr/bin/env python3

"""
This module is used to update all Proactive Remediation in Intune.
"""

import json
import os
import base64

from deepdiff import DeepDiff
from .graph_request import makeapirequest, makeapirequestPatch, makeapirequestPost
from .graph_batch import batch_assignment, get_object_assignment
from .update_assignment import update_assignment, post_assignment_update
from .check_file import check_file
from .load_file import load_file
from .remove_keys import remove_keys
from .get_diff_output import get_diff_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceHealthScripts"


def update(path, token, assignment=False):
    """
    This function updates all Proactive Remediation in Intune if,
    the configuration in Intune differs from the JSON/YAML file.

    :param path: Path to where the backup is saved
    :param token: Token to use for authenticating the request
    :param assignment: Boolean to determine if assignments should be updated
    """

    diff_count = 0
    # Set Powershell script path
    configpath = f'{path}/Proactive Remediations'
    # If Powershell script path exists, continue
    if os.path.exists(configpath):
        # Get Proactive remediation's
        mem_proactiveRemediation = makeapirequest(ENDPOINT, token)
        # Get current assignment
        mem_assignments = batch_assignment(
            mem_proactiveRemediation,
            'deviceManagement/deviceHealthScripts/',
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

                data = {'value': ''}
                if mem_proactiveRemediation['value']:
                    for val in mem_proactiveRemediation['value']:
                        if repo_data['displayName'] == val['displayName']:
                            data['value'] = val

                # If Powershell script exists, continue
                if data['value']:
                    print("-" * 90)
                    q_param = None
                    # Get Powershell script details
                    mem_data = makeapirequest(
                        ENDPOINT + "/" + data['value']['id'], token, q_param)
                    mem_id = data['value']['id']
                    # Remove keys before using DeepDiff
                    mem_data = remove_keys(mem_data)

                    # Check if script data is saved and read the file
                    detection_script_name = f"{configpath}/Script Data/{repo_data['displayName']}_DetectionScript.ps1"
                    remediation_script_name = f"{configpath}/Script Data/{repo_data['displayName']}_RemediationScript.ps1"
                    if os.path.exists(detection_script_name) and os.path.exists(
                            remediation_script_name):
                        with open(detection_script_name, 'r') as df:
                            repo_detection_config = df.read()
                        with open(remediation_script_name, 'r') as rf:
                            repo_remediation_config = rf.read()

                        mem_detection_config = base64.b64decode(
                            mem_data['detectionScriptContent']).decode('utf-8')
                        mem_remediation_config = base64.b64decode(
                            mem_data['remediationScriptContent']).decode('utf-8')

                        ddiff = DeepDiff(
                            mem_detection_config,
                            repo_detection_config,
                            ignore_order=True).get(
                            'values_changed',
                            {})
                        rdiff = DeepDiff(
                            mem_remediation_config,
                            repo_remediation_config,
                            ignore_order=True).get(
                            'values_changed',
                            {})
                        cdiff = DeepDiff(
                            mem_data,
                            repo_data,
                            ignore_order=True,
                            exclude_paths=[
                                "root['detectionScriptContent']",
                                "root['remediationScriptContent']"]).get(
                            'values_changed',
                            {})

                        # If any changed values are found, push them to Intune
                        if cdiff or ddiff or rdiff:
                            print(
                                "Updating Proactive Remediation: " +
                                repo_data['displayName'] +
                                ", values changed:")
                            if cdiff:
                                diff_count += 1
                                values = get_diff_output(cdiff)
                                for value in values:
                                    print(value)
                            if ddiff:
                                diff_count += 1
                                print(
                                    "Detection script changed, check commit history for change details")
                            if rdiff:
                                diff_count += 1
                                print(
                                    "Remediation script changed, check commit history for change details")
                            detection_bytes = repo_detection_config.encode(
                                'utf-8')
                            remediation_bytes = repo_remediation_config.encode(
                                'utf-8')
                            repo_data['detectionScriptContent'] = base64.b64encode(
                                detection_bytes).decode('utf-8')
                            repo_data['remediationScriptContent'] = base64.b64encode(
                                remediation_bytes).decode('utf-8')
                            request_data = json.dumps(repo_data)
                            q_param = None
                            makeapirequestPatch(
                                ENDPOINT + "/" + mem_id, token, q_param, request_data)
                        else:
                            print(
                                'No difference found for Proactive Remediation: ' +
                                repo_data['displayName'])

                    if assignment:
                        mem_assign_obj = get_object_assignment(
                            mem_id, mem_assignments)
                        update = update_assignment(
                            assign_obj, mem_assign_obj, token)
                        if update is not None:
                            request_data = {'deviceHealthScriptAssignments': update}
                            post_assignment_update(
                                request_data, mem_id, 'deviceManagement/deviceHealthScripts', 'assign', token)

                            # If Powershell script does not exist, create it
                            # and assign
                else:
                    print("-" * 90)
                    print("Proactive Remediation not found, creating: " +
                          repo_data['displayName'])
                    request_json = json.dumps(repo_data)
                    post_request = makeapirequestPost(
                        ENDPOINT, token, q_param=None, jdata=request_json, status_code=201)
                    mem_assign_obj = []
                    assignment = update_assignment(
                        assign_obj, mem_assign_obj, token)
                    if assignment is not None:
                        request_data = {'deviceHealthScriptAssignments': assignment}
                        post_assignment_update(
                            request_data,
                            post_request['id'],
                            'deviceManagement/deviceHealthScripts',
                            'assign',
                            token)
                    print(
                        "Proactive Remediation created with id: " +
                        post_request['id'])

    return diff_count
