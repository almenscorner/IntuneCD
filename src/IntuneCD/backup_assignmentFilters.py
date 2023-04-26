#!/usr/bin/env python3

"""
This module backs up all Filters in Intune.
"""

from .clean_filename import clean_filename
from .graph_request import makeapirequest
from .save_output import save_output
from .remove_keys import remove_keys

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/assignmentFilters"


# Get all Filters and save them in specified path
def savebackup(path, output, token):
    """
    Saves all Filter in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    results = {"config_count": 0, "outputs": []}
    configpath = path + "/" + "Filters/"
    data = makeapirequest(ENDPOINT, token)

    if data:
        for assign_filter in data["value"]:
            results["config_count"] += 1
            assign_filter = remove_keys(assign_filter)
            print("Backing up Filter: " + assign_filter["displayName"])

            # Get filename without illegal characters
            fname = clean_filename(assign_filter["displayName"])
            # Save Filters as JSON or YAML depending on configured value in
            # "-o"
            save_output(output, configpath, fname, assign_filter)

            results["outputs"].append(fname)

    return results
