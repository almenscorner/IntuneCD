# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class SecurityDefaultsBackupModule(BaseBackupModule):
    """A class used to backup Entra Security Defaults

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/v1.0/policies/identitySecurityDefaultsEnforcementPolicy"

    def __init__(self, *args, **kwargs):
        """Initializes the SecurityDefaultsBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Entra/Security Defaults/"
        self.preset_filename = "security_defaults"

    def main(self) -> dict[str, any]:
        """The main method to backup the Entra data

        Returns:
            dict[str, any]: The results of the backup
        """

        try:
            self.entra_data = self.make_graph_request(
                self.endpoint + self.CONFIG_ENDPOINT
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Security Defaults data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        self.log(msg="Backing up Entra Security Defaults")

        try:
            self.results = self.process_data(
                data=self.entra_data,
                filetype=self.filetype,
                path=self.path,
                name_key="",
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing Security Defaults data: {e}")
            return None

        return self.results
