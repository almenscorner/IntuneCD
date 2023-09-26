#!/usr/bin/env python3

"""
This module backs up all Enrollment Configurations in Intune.
"""

import re

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .save_output import save_output
from .remove_keys import remove_keys
from .graph_batch import batch_assignment, get_object_assignment
from .check_prefix import check_prefix_match

# Set MS Graph endpoint
ENDPOINT = (
    "https://graph.microsoft.com/beta/deviceManagement/deviceEnrollmentConfigurations"
)


# Get all Enrollment Configurations and save them in specified path
def savebackup(path, output, exclude, token, prefix):
    """
    Saves all Enrollment Configurations in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    configpath = path + "/" + "Enrollment Configurations/"
    data = makeapirequest(ENDPOINT, token)

    assignment_responses = batch_assignment(
        data, "deviceManagement/deviceEnrollmentConfigurations/", "/assignments", token
    )

    for config in data["value"]:
        if prefix and not check_prefix_match(config["displayName"], prefix):
            continue

        if (
            config["@odata.type"]
            == "#microsoft.graph.windows10EnrollmentCompletionPageConfiguration"
        ):
            continue
        results["config_count"] += 1
        config_type = config.get("deviceEnrollmentConfigurationType", None)
        config_type = config_type[0].upper() + config_type[1:]
        config_type = re.findall("[A-Z][^A-Z]*", config_type)
        config_type = " ".join(config_type)

        print(f"Backing up Enrollment Config {config_type}: " + config["displayName"])

        if "assignments" not in exclude:
            assignments = get_object_assignment(config["id"], assignment_responses)
            if assignments:
                config["assignments"] = assignments

        fname = clean_filename(
            f"{config['displayName']}_{str(config['@odata.type']).split('.')[2]}"
        )

        config = remove_keys(config)

        # Get filename without illegal characters
        fname = clean_filename(fname)
        # Save Enrollment Configuration as JSON or YAML depending on configured
        # value in "-o"
        save_output(output, configpath, fname, config)

        results["outputs"].append(fname)

    return results
