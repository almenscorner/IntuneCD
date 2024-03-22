# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class EnrollmentConfigurationsBackupModule(BaseBackupModule):
    """A class used to backup Intune Enrollment Configurations

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceEnrollmentConfigurations/"
    LOG_MESSAGE = "Backing up Enrollment Configuration: "

    def __init__(self, *args, **kwargs):
        """Initializes the EnrollmentConfigurationsBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Enrollment Configurations/"
        self.assignment_endpoint = "deviceManagement/deviceEnrollmentConfigurations/"
        self.assignment_extra_url = "/assignments"
        self.audit_filter = "componentName eq 'Enrollment'"

    def main(self) -> dict[str, any]:
        """The main method to backup the Enrollment Configurations

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
                msg=f"Error getting Enrollment Configuration data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        # Remove the windows10EnrollmentCompletionPageConfiguration from the data
        self.graph_data = [
            item
            for item in self.graph_data["value"]
            if item["@odata.type"]
            != "#microsoft.graph.windows10EnrollmentCompletionPageConfiguration"
        ]

        try:
            self.results = self.process_data(
                data=self.graph_data,
                filetype=self.filetype,
                path=self.path,
                name_key="displayName",
                log_message=self.LOG_MESSAGE,
                audit_compare_info={"type": "resourceId", "value_key": "id"},
            )
        except Exception as e:
            self.log(
                tag="error", msg=f"Error processing Enrollment Configuration data: {e}"
            )
            return None

        return self.results
