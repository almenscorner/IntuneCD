# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class B2BPolicyBackupModule(BaseBackupModule):
    """A class used to backup Entra B2B Policy

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "B2B/b2bPolicy"

    def __init__(self, *args, **kwargs):
        """Initializes the B2BPolicyBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Entra/External Collaboration Settings/"
        self.preset_filename = "b2b_policy"

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
                msg=f"Error getting External Collaboration Settings data from {self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        self.log(msg="Backing up Entra External Collaboration Settings B2B Policy")

        try:
            self.results = self.process_data(
                data=self.entra_data,
                filetype=self.filetype,
                path=self.path,
                name_key="",
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error processing External Collaboration Settings data: {e}",
            )
            return None

        return self.results
