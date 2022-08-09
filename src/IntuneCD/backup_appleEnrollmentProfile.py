#!/usr/bin/env python3

"""
This module backs up all Apple Enrollment Profiles in Intune.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .graph_batch import batch_request
from .save_output import save_output
from .remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/depOnboardingSettings/"


# Get all Apple Enrollment Profiles and save them in specified path
def savebackup(path, output, token):
    """
    Saves all Apple Enrollment Profiles in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    config_count = 0
    configpath = path + "/" + "Enrollment Profiles/Apple/"
    data = makeapirequest(ENDPOINT, token)

    if data['value']:
        profile_ids = []
        for profile in data['value']:
            profile_ids.append(profile['id'])

        batch_profile_data = batch_request(
            profile_ids,
            'deviceManagement/depOnboardingSettings/',
            '/enrollmentProfiles',
            token)

        for profile in batch_profile_data:
            config_count += 1
            for value in profile['value']:
                value = remove_keys(value)

                print(
                    "Backing up Apple enrollment profile: " +
                    value['displayName'])

                # Get filename without illegal characters
                fname = clean_filename(value['displayName'])
                # Save Apple Enrollment Profile as JSON or YAML depending on
                # configured value in "-o"
                save_output(output, configpath, fname, value)

    return config_count
