#!/usr/bin/env python3

"""
This module backs up all Windows Enrollment Profiles in Intune.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .graph_batch import batch_assignment, get_object_assignment
from .save_output import save_output
from .remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/windowsAutopilotDeploymentProfiles"


# Get all Windows Enrollment Profiles and save them in specified path
def savebackup(path, output, exclude, token):
    """
    Saves all Windows Enrollment Profiles in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    config_count = 0
    configpath = path + "/" + "Enrollment Profiles/Windows/"
    data = makeapirequest(ENDPOINT, token)

    assignment_responses = batch_assignment(
        data,
        'deviceManagement/windowsAutopilotDeploymentProfiles/',
        '/assignments',
        token)

    for profile in data['value']:
        config_count += 1
        if "assignments" not in exclude:
            assignments = get_object_assignment(
                profile['id'], assignment_responses)
            if assignments:
                profile['assignments'] = assignments

        profile = remove_keys(profile)

        print("Backing up Autopilot enrollment profile: " +
              profile['displayName'])

        # Get filename without illegal characters
        fname = clean_filename(profile['displayName'])
        # Save Windows Enrollment Profile as JSON or YAML depending on
        # configured value in "-o"
        save_output(output, configpath, fname, profile)

    return config_count
