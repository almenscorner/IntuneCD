# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class AuthorizationPolicyBackupModule(BaseBackupModule):
    """A class used to backup Entra Authorization Policy

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/policies/authorizationPolicy"

    def __init__(self, *args, **kwargs):
        """Initializes the AuthorizationPolicyBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Entra/Authorization Policy/"
        self.preset_filename = "authorization_policy"

    def main(self) -> dict[str, any]:
        """The main method to backup the Entra data

        Returns:
            dict[str, any]: The results of the backup
        """

        try:
            self.entra_data = self.make_graph_request(
                endpoint=self.endpoint + self.CONFIG_ENDPOINT
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Authorization Policy data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        self.log(msg="Backing up Entra Authorization Policy")

        try:
            self.results = self.process_data(
                data=self.entra_data["value"],
                filetype=self.filetype,
                path=self.path,
                name_key="",
            )
        except Exception as e:
            self.log(
                tag="error", msg=f"Error processing Authorization Policy data: {e}"
            )
            return None

        return self.results
