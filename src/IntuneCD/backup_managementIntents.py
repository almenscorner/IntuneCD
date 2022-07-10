#!/usr/bin/env python3

"""
This module backs up all Intents in Intune.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .graph_batch import batch_intents, get_object_assignment, batch_assignment
from .save_output import save_output

# Set MS Graph base endpoint
BASE_ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement"
TEMPLATE_ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/templates"


# Get all Intents and save them in specified path
def savebackup(path, output, exclude, token):
    """
    Saves all Intents in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    config_count = 0
    configpath = path + "/" + "Management Intents/"
    intents = makeapirequest(BASE_ENDPOINT + "/intents", token)
    templates = makeapirequest(TEMPLATE_ENDPOINT, token)

    assignment_responses = batch_assignment(
        intents, 'deviceManagement/intents/', '/assignments', token)
    intent_responses = batch_intents(intents, token)

    if intent_responses:
        for intent_value in intent_responses['value']:
            config_count += 1
            print("Backing up Intent: " + intent_value['displayName'])

            for template in templates['value']:
                if intent_value['templateId'] == template['id']:
                    template_type = template['displayName']

            configpath = path + "/" + "Management Intents/" + \
                template_type + "/"

            if "assignments" not in exclude:
                assignments = get_object_assignment(
                    intent_value['id'], assignment_responses)
                if assignments:
                    intent_value['assignments'] = assignments

            for setting in intent_value['settingsDelta']:
                setting.pop('id', None)
            intent_value.pop('id', None)

            # Get filename without illegal characters
            fname = clean_filename(intent_value['displayName'])
            # Save Intent as JSON or YAML depending on configured value in "-o"
            save_output(output, configpath, fname, intent_value)

    return config_count
