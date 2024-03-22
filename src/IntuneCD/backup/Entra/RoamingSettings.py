# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class RoamingSettingsBackupModule(BaseBackupModule):
    """A class used to backup Entra Roaming Settings

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "RoamingSettings?ESRV2=true"

    def __init__(self, *args, **kwargs):
        """Initializes the RoamingSettingsBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Entra/Roaming Settings/"
        self.preset_filename = "roaming_settings"

    def main(self) -> dict[str, any]:
        """The main method to backup the Entra data

        Returns:
            dict[str, any]: The results of the backup
        """

        try:
            self.entra_data = self.make_azure_request(
                endpoint=self.CONFIG_ENDPOINT,
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Roaming Settings data from {self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        self.log(msg="Backing up Entra Roaming Settings")

        try:
            self.results = self.process_data(
                data=self.entra_data,
                filetype=self.filetype,
                path=self.path,
                name_key="",
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing Roaming Settings data: {e}")
            return None

        return self.results
