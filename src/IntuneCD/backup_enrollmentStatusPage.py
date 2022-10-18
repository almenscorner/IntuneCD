#!/usr/bin/env python3

"""
This module backs up all Windows Enrollment Status Page profiles.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .graph_batch import batch_assignment, get_object_assignment
from .save_output import save_output
from .remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/deviceEnrollmentConfigurations"
APP_ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"


# Get all Windows Enrollment Status Page profiles and save them in specified path
def savebackup(path, output, exclude, token):
    """
    Saves all Windows Enrollment Status Page profiles in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    config_count = 0
    configpath = path + "/" + "Enrollment Profiles/Windows/ESP/"
    data = makeapirequest(ENDPOINT, token)

    assignment_responses = batch_assignment(
        data,
        'deviceManagement/deviceEnrollmentConfigurations/',
        '/assignments',
        token)

    for profile in data['value']:
        if profile['@odata.type'] == "#microsoft.graph.windows10EnrollmentCompletionPageConfiguration":
            config_count += 1
            if "assignments" not in exclude:
                assignments = get_object_assignment(
                    profile['id'], assignment_responses)
                if assignments:
                    profile['assignments'] = assignments

            profile = remove_keys(profile)

            # If the profile contains apps, get the name of the app
            if 'selectedMobileAppIds' in profile:
                app_ids = profile['selectedMobileAppIds']
                app_names = []
                for app_id in app_ids:
                    app_data = makeapirequest(APP_ENDPOINT + "/" + app_id, token)
                    app = {'name': app_data['displayName'], 'type': app_data['@odata.type']}
                    app_names.append(app)
                if app_names:
                    profile.pop('selectedMobileAppIds', None)
                    profile['selectedMobileAppNames'] = app_names

            print("Backing up Enrollment Status Page: " +
                profile['displayName'])

            # Get filename without illegal characters
            fname = clean_filename(profile['displayName'])
            # Save Windows Enrollment Profile as JSON or YAML depending on
            # configured value in "-o"
            save_output(output, configpath, fname, profile)

    return config_count
