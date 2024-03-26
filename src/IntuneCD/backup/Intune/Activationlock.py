# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class ActivationLockBackupModule(BaseBackupModule):
    """A class used to backup Intune Activation Lock Bypass Codes

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/managedDevices"
    LOG_MESSAGE = "Backing up "

    def __init__(self, *args, **kwargs):
        """Initializes the ActivationLockBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Activation Lock Bypass Codes/"
        self.append_id = False
        self.audit = False
        self.prefix = None
        self.preset_filename = "activation_lock_bypass_codes"
        self.has_assignments = False

    def main(self) -> None:
        """The main method to backup the Activation Lock Bypass Codes"""
        self.log(msg="Backing up Activation Lock Bypass Codes")

        try:
            self.graph_data = self.make_graph_request(
                endpoint=self.endpoint + self.CONFIG_ENDPOINT,
                params={
                    "$select": "id",
                    "$filter": "startsWith(operatingSystem, 'macOS') or startsWith(operatingSystem, 'iOS') or startsWith(operatingSystem, 'iPadOS')",
                },
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Activation Lock data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        device_ids = [device["id"] for device in self.graph_data["value"]]
        device_data = self.batch_request(
            device_ids,
            "deviceManagement/managedDevices/",
            "?$select=id,deviceName,serialNumber,activationLockBypassCode",
        )
        devices = [
            {k: v for k, v in d.items() if k != "@odata.context"}
            for d in device_data
            if d["activationLockBypassCode"] is not None
        ]

        try:
            self.process_data(
                data=devices,
                filetype=self.filetype,
                path=self.path,
                name_key=None,
                log_message=None,
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing Activation Lock data: {e}")
            return None
