#!/usr/bin/env python3

"""
This module backs up all Configuration Policies in Intune.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .graph_batch import batch_assignment, get_object_assignment, batch_request, get_object_details
from .save_output import save_output
from .remove_keys import remove_keys

# Set MS Graph base endpoint
BASE_ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement"


# Get all Configuration Policies and save them in specified path
def savebackup(path, output, exclude, token):
    """
    Saves all Configuration Policies in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param exclude: If "assignments" is in the list, it will not back up the assignments
    :param token: Token to use for authenticating the request
    """

    config_count = 0
    configpath = path + "/" + "Settings Catalog/"
    policies = makeapirequest(BASE_ENDPOINT + "/configurationPolicies", token)
    policy_ids = []
    for policy in policies['value']:
        policy_ids.append(policy['id'])

    assignment_responses = batch_assignment(
        policies,
        'deviceManagement/configurationPolicies/',
        '/assignments',
        token)
    policy_settings_batch = batch_request(
        policy_ids,
        'deviceManagement/configurationPolicies/',
        '/settings',
        token)

    for policy in policies['value']:
        config_count += 1
        name = policy['name']
        print("Backing up configuration policy: " + name)

        settings = get_object_details(policy['id'], policy_settings_batch)

        if settings:
            policy['settings'] = settings

        if "assignments" not in exclude:
            assignments = get_object_assignment(
                policy['id'], assignment_responses)
            if assignments:
                policy['assignments'] = assignments

        policy = remove_keys(policy)

        # Get filename without illegal characters
        fname = clean_filename(name)
        # Save Configuration Policy as JSON or YAML depending on configured
        # value in "-o"
        save_output(output, configpath, fname, policy)

    return config_count
