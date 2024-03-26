# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class DomainsBackupModule(BaseBackupModule):
    """A class used to backup Entra Domains

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/domains"

    def __init__(self, *args, **kwargs):
        """Initializes the DomainsBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Entra/Domains/"
        self.clean_data = False

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
                msg=f"Error getting Domain data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        self.log(msg="Backing up Entra Domains")

        try:
            self.results = self.process_data(
                data=self.entra_data["value"],
                filetype=self.filetype,
                path=self.path,
                name_key="id",
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing Domains data: {e}")
            return None

        return self.results
