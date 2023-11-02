#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up all Autopilot devices in Intune.
"""

from ...intunecdlib.clean_filename import clean_filename
from ...intunecdlib.graph_request import makeapirequest
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = (
    "https://graph.microsoft.com/beta/deviceManagement/windowsAutopilotDeviceIdentities"
)


# Get all Autopilot devices and save them in specified path
def savebackup(path, output, token):
    """
    Saves all Autopilot devices in Intune to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    print("Backing up Autopilot Devices")
    configpath = path + "/" + "Autopilot Devices/"
    data = makeapirequest(ENDPOINT, token)

    for device in data["value"]:
        # Get filename without illegal characters
        fname = clean_filename(device["id"])
        # Save Autopilot device as JSON or YAML depending on configured
        # value in "-o"
        save_output(output, configpath, fname, device)
