# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class VPPBackupModule(BaseBackupModule):
    """A class used to backup Intune VPP Tokens

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceAppManagement/vppTokens"
    LOG_MESSAGE = "Backing up VPP Token: "

    def __init__(self, *args, **kwargs):
        """Initializes the VPPBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Apple VPP Tokens/"
        self.audit_filter = self.audit_filter or "componentName eq 'MobileApp'"
        # VPP tokens has no assignments, so exclude assignments from the run
        self.has_assignments = False

    def main(self) -> dict[str, any]:
        """The main method to backup the VPP Tokens

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
                msg=f"Error getting VPP Token data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        try:
            self.results = self.process_data(
                data=self.graph_data["value"],
                filetype=self.filetype,
                path=self.path,
                name_key="displayName",
                log_message=self.LOG_MESSAGE,
                audit_compare_info={
                    "type": "resourceId",
                    "value_key": "id",
                },
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing VPP Token data: {e}")
            return None

        return self.results
