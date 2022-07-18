#!/usr/bin/env python3

"""
This module backs up all Proactive Remediation in Intune.
"""

import os
import base64

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .graph_batch import batch_assignment, get_object_assignment, batch_request
from .save_output import save_output
from .remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceHealthScripts"


# Get all Proactive Remediation and save them in specified path
def savebackup(path, output, exclude, token):
    """
    Saves all Proactive Remediation in Intune to a JSON or YAML file and script files.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    config_count = 0
    configpath = f'{path}/Proactive Remediations/'
    data = makeapirequest(ENDPOINT, token)
    if data['value']:
        pr_ids = []
        for script in data['value']:
            pr_ids.append(script['id'])

        assignment_responses = batch_assignment(
            data, 'deviceManagement/deviceHealthScripts/', '/assignments', token)
        pr_data_responses = batch_request(
            pr_ids, 'deviceManagement/deviceHealthScripts/', '', token)

        for pr_details in pr_data_responses:
            if "Microsoft" not in pr_details['publisher']:
                config_count += 1
                if "assignments" not in exclude:
                    assignments = get_object_assignment(
                        pr_details['id'], assignment_responses)
                    if assignments:
                        pr_details['assignments'] = assignments

                pr_details = remove_keys(pr_details)

                print(
                    f"Backing up Proactive Remediation: {pr_details['displayName']}")

                # Get filename without illegal characters
                fname = clean_filename(pr_details['displayName'])

                # Save Proactive Remediation as JSON or YAML depending on
                # configured value in "-o"
                save_output(output, configpath, fname, pr_details)

                if not os.path.exists(f'{configpath}/Script Data'):
                    os.makedirs(f'{configpath}/Script Data')

                # Save detection script to the Script Data folder
                config_count += 1
                decoded = base64.b64decode(
                    pr_details['detectionScriptContent']).decode('utf-8')
                f = open(
                    f"{configpath}/Script Data/{pr_details['displayName']}_DetectionScript.ps1",
                    'w')
                f.write(decoded)
                # Save remediation script to the Script Data folder
                config_count += 1
                decoded = base64.b64decode(
                    pr_details['remediationScriptContent']).decode('utf-8')
                f = open(
                    f"{configpath}/Script Data/{pr_details['displayName']}_RemediationScript.ps1",
                    'w')
                f.write(decoded)

    return config_count
