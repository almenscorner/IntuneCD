# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class TemplateBackupModule(BaseBackupModule):
    """A class used to backup Intune {config_type}

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/Template"  # TODO: Change this to the endpoint to get the data from
    LOG_MESSAGE = "Backing up Template: "  # TODO: Change this to the message to log when backing up the data

    def __init__(self, *args: any, **kwargs: any) -> None:
        """Initializes the {config_type}BackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = (
            f"{self.path}/Template/"  # TODO: Change this to the path to backup the data
        )
        self.audit_filter = "componentName eq 'Template'"  # TODO: Change this to the audit filter applicable to the data
        self.assignment_endpoint = "deviceManagement/Template/"  # TODO: Change this to the endpoint to get the assignments from
        self.assignment_extra_url = "/assignments"
        self.prefix = None  # TODO: Remove this line if data should be prefixed
        self.has_assignments = (
            False  # TODO: Remove this line if the data has assignments
        )

    def main(self) -> dict[str, any]:
        """The main method to backup the Scope Tags

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
                msg=f"Error getting Template data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
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
                },  # TODO: Change this to the audit compare info applicable to the data
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing Template data: {e}")
            return None

        return self.results
