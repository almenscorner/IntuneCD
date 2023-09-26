#!/usr/bin/env python3

"""
This module backs up all Notification Templates in Intune.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .save_output import save_output
from .remove_keys import remove_keys
from .check_prefix import check_prefix_match

# Set MS Graph endpoint
ENDPOINT = (
    "https://graph.microsoft.com/beta/deviceManagement/notificationMessageTemplates"
)


# Get all Notification Templates and save them in specified path
def savebackup(path, output, token, prefix):
    """
    Saves all Notification Templates in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    configpath = path + "/" + "Compliance Policies/Message Templates/"
    q_param = "?$expand=localizedNotificationMessages"
    data = makeapirequest(ENDPOINT, token, q_param)

    for template in data["value"]:
        if prefix and not check_prefix_match(template["displayName"], prefix):
            continue

        results["config_count"] += 1
        print("Backing up Notification message template: " + template["displayName"])
        q_param = "?$expand=localizedNotificationMessages"
        template_data = makeapirequest(ENDPOINT + "/" + template["id"], token, q_param)

        template_data = remove_keys(template_data)

        for locale in template_data["localizedNotificationMessages"]:
            remove_keys(locale)

        # Get filename without illegal characters
        fname = clean_filename(template_data["displayName"])
        # Save Notification template as JSON or YAML depending on configured
        # value in "-o"
        save_output(output, configpath, fname, template_data)

        results["outputs"].append(fname)

    return results
