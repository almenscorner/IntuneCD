# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class DeviceManagementSettingsBackupModule(BaseBackupModule):
    """A class used to backup Intune Device Management Settings

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/settings"

    def __init__(self, *args, **kwargs):
        """Initializes the DeviceManagementSettingsBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Device Management Settings/"
        self.append_id = False
        self.audit_filter = self.audit_filter or (
            "resources/any(s:s/auditResourceType eq 'DeviceManagementSettings')"
        )
        # Set the filename to settings
        self.preset_filename = "settings"
        # Device management settings has no assignments, so exclude assignments from the run
        self.has_assignments = False

    def main(self) -> dict[str, any]:
        """The main method to backup the Device Management Settings

        Returns:
            dict[str, any]: The results of the backup
        """
        try:
            self.graph_data = self.make_graph_request(
                endpoint=self.endpoint + self.CONFIG_ENDPOINT
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Device Management Settings data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        self.log(msg="Backing up Device Management Settings")

        try:
            self.results = self.process_data(
                data=self.graph_data,
                filetype=self.filetype,
                path=self.path,
                name_key="",
                log_message=None,
                audit_compare_info={
                    "type": "auditResourceType",
                    "value_key": "Microsoft.Management.Services.Api.ApplePushNotificationCertificate",
                },
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error processing Device Management Settings data: {e}",
            )
            return None

        return self.results
