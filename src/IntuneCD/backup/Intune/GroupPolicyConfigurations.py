# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class GroupPolicyConfigurationsBackupModule(BaseBackupModule):
    """A class used to backup Intune Group Policy Configurations

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/groupPolicyConfigurations"
    LOG_MESSAGE = "Backing up Device Configuration: "

    def __init__(self, *args, **kwargs):
        """Initializes the GroupPolicyConfigurationsBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Group Policy Configurations/"
        self.audit_filter = "componentName eq 'DeviceConfiguration'"
        self.assignment_endpoint = "deviceManagement/groupPolicyConfigurations/"
        self.assignment_extra_url = "/assignments"

    def main(self) -> dict[str, any]:
        """The main method to backup the Group Policy Configurations

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
                msg=f"Error getting Group Policy Configuration data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        for item in self.graph_data["value"]:
            definition_endpoint = f"{self.endpoint}{self.CONFIG_ENDPOINT}/{item['id']}/definitionValues?$expand=definition"
            # Get definitions
            definitions = self.make_graph_request(endpoint=definition_endpoint)

            if definitions:
                item["definitionValues"] = definitions["value"]
                for definition in item["definitionValues"]:
                    presentation_endpoint = (
                        f"{self.endpoint}{self.CONFIG_ENDPOINT}/{item['id']}/definitionValues/{definition['id']}/"
                        f"presentationValues?$expand=presentation"
                    )
                    presentation = self.make_graph_request(
                        endpoint=presentation_endpoint
                    )
                    definition["presentationValues"] = presentation["value"]

        try:
            self.results = self.process_data(
                data=self.graph_data["value"],
                filetype=self.filetype,
                path=self.path,
                name_key="displayName",
                log_message=self.LOG_MESSAGE,
                audit_compare_info={"type": "resourceId", "value_key": "id"},
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error processing Group Policy Configuration data: {e}",
            )
            return None

        return self.results
