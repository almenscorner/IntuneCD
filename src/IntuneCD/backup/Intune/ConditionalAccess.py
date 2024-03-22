# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class ConditionalAccessBackupModule(BaseBackupModule):
    """A class used to backup Conditional Access policies

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/identity/conditionalAccess/policies"
    LOG_MESSAGE = "Backing up Conditional Access Policy: "

    def __init__(self, *args, **kwargs):
        """Initializes the ConditionalAccessBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Conditional Access/"
        self.audit = False
        # Skip assignments on this module
        self.has_assignments = False

    def main(self) -> dict[str, any]:
        """The main method to backup the Conditional Access policies

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
                msg=f"Error getting Conditional Access Policy data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        for item in self.graph_data["value"]:
            # Remove the keys that are not needed from each grantControls
            if item.get("grantControls"):
                item["grantControls"].pop("authenticationStrength@odata.context", None)

        try:
            self.results = self.process_data(
                data=self.graph_data["value"],
                filetype=self.filetype,
                path=self.path,
                name_key="displayName",
                log_message=self.LOG_MESSAGE,
            )
        except Exception as e:
            self.log(
                tag="error", msg=f"Error processing Conditional Access Policy data: {e}"
            )
            return None

        return self.results
