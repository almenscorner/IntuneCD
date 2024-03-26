# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class AuthenticationFlowsBackupModule(BaseBackupModule):
    """A class used to backup Entra Authentication Flows

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/policies/authenticationFlowsPolicy"

    def __init__(self, *args, **kwargs):
        """Initializes the AuthenticationFlowsBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Entra/Authentication Flows Policy/"
        self.preset_filename = "authentication_flows_policy"

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
                msg=f"Error getting Authentication Flows data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        self.log(msg="Backing up Entra Authentication Flows")

        try:
            self.results = self.process_data(
                data=self.entra_data,
                filetype=self.filetype,
                path=self.path,
                name_key="",
            )
        except Exception as e:
            self.log(
                tag="error", msg=f"Error processing Authentication Flows data: {e}"
            )
            return None

        return self.results
