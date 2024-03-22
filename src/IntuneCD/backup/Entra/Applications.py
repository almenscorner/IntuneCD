# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class ApplicationsBackupModule(BaseBackupModule):
    """A class used to backup Entra Applications

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/v1.0/myorganization/applications"
    LOG_MESSAGE = "Backing up Entra Application: "

    def __init__(self, *args, **kwargs):
        """Initializes the ApplicationsBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Entra/Applications/"
        self.handle_assignment = False

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
                msg=f"Error getting Application data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        try:
            self.results = self.process_data(
                data=self.entra_data["value"],
                filetype=self.filetype,
                path=self.path,
                name_key="displayName",
                log_message=self.LOG_MESSAGE,
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing Application data: {e}")
            return None

        return self.results
