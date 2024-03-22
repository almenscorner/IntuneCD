# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class SSPRBackupModule(BaseBackupModule):
    """A class used to backup Entra SSPR

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "PasswordReset/PasswordResetPolicies"

    def __init__(self, *args, **kwargs):
        """Initializes the SSPRBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Entra/Password Reset Policies/"
        self.preset_filename = "password_reset_policies"

    def main(self) -> dict[str, any]:
        """The main method to backup the Entra data

        Returns:
            dict[str, any]: The results of the backup
        """

        try:
            self.entra_data = self.make_azure_request(self.CONFIG_ENDPOINT)
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Password Reset Policies data from {self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        self.log(msg="Backing up Entra Password Reset Policies")

        try:
            self.results = self.process_data(
                data=self.entra_data,
                filetype=self.filetype,
                path=self.path,
                name_key="",
            )
        except Exception as e:
            self.log(
                tag="error", msg=f"Error processing Password Reset Policies data: {e}"
            )
            return None

        return self.results
