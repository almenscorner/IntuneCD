#!/usr/bin/env python3

"""
This module backs up all App Configuration Polices in Intune.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .graph_batch import batch_assignment, get_object_assignment
from .save_output import save_output
from .remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileAppConfigurations"
APP_ENDPOINT = "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"


# Get all App Configuration policies and save them in specified path
def savebackup(path, output, exclude, token):
    """
    Saves all App Configuration policies in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    config_count = 0
    configpath = path + "/" + "App Configuration/"
    data = makeapirequest(ENDPOINT, token)

    if data['value']:

        assignment_responses = batch_assignment(
            data, 'deviceAppManagement/mobileAppConfigurations/', '/assignments', token)

        for profile in data['value']:
            config_count += 1
            if "assignments" not in exclude:
                assignments = get_object_assignment(
                    profile['id'], assignment_responses)
                if assignments:
                    profile['assignments'] = assignments

            profile = remove_keys(profile)

            # Get name and type of app on App Configuration Profile
            app_dict = {}
            for app_id in profile['targetedMobileApps']:
                app_data = makeapirequest(APP_ENDPOINT + "/" + app_id, token)
                if app_data:
                    app_dict['appName'] = app_data['displayName']
                    app_dict['type'] = app_data['@odata.type']

            if app_dict:
                profile.pop('targetedMobileApps')
                profile['targetedMobileApps'] = app_dict

            print("Backing up App Configuration: " + profile['displayName'])

            # Get filename without illegal characters
            fname = clean_filename(
                f"{profile['displayName']}_{str(profile['@odata.type'].split('.')[2])}")
            # Save App Configuration as JSON or YAML depending on configured value
            # in "-o"
            save_output(output, configpath, fname, profile)

    return config_count
