#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module backs up Activation Lock Codes setting in Intune.
"""

from ...intunecdlib.graph_batch import batch_request
from ...intunecdlib.graph_request import makeapirequest
from ...intunecdlib.save_output import save_output

# Set MS Graph endpoint
ENDPOINT = "https://graph.microsoft.com/beta/deviceManagement/managedDevices"


# Get Activation Lock Codes information and save in specified path
def savebackup(path, output, token):
    """
    Save Activation Lock Codes setting to a JSON or YAML file.

    :param path: Path to save the backup to
    :param output: Format the backup will be saved as
    :param token: Token to use for authenticating the request
    """

    configpath = path + "/" + "Activation Lock Bypass Codes/"
    q_params = {
        "$select": "id",
        "$filter": "startsWith(operatingSystem, 'macOS') or startsWith(operatingSystem, 'iOS') or startsWith(operatingSystem, 'iPadOS')",
    }
    data = makeapirequest(ENDPOINT, token, q_params)

    if data["value"]:
        device_ids = [device["id"] for device in data["value"]]
        print("Backing up Activation Lock Bypass Codes")

        device_data = batch_request(
            device_ids,
            "deviceManagement/managedDevices/",
            "?$select=id,deviceName,serialNumber,activationLockBypassCode",
            token,
        )

        # Get all devices with Activation Lock Codes without the context key
        devices = [
            {k: v for k, v in d.items() if k != "@odata.context"}
            for d in device_data
            if d["activationLockBypassCode"] is not None
        ]

        # Get filename without illegal characters
        fname = "activation_lock_bypass_codes"
        # Save Activation Lock Codes as JSON or YAML depending on configured value in "-o"
        if devices:
            save_output(output, configpath, fname, devices)
