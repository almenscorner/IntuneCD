# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class ManagementIntentsBackupModule(BaseBackupModule):
    """A class used to backup Intune Management Intents

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        TEMPALETE_ENDPOINT (str): The endpoint to get the template data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement"
    TEMPALETE_ENDPOINT = "/beta/deviceManagement/templates"
    LOG_MESSAGE = "Backing up Management intent: "

    def __init__(self, *args, **kwargs):
        """Initializes the ManagementIntentsBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Management Intents/"
        self.audit_filter = "componentName eq 'DeviceIntent'"
        self.assignment_endpoint = "deviceManagement/intents/"
        self.assignment_extra_url = "/assignments"

    def main(self) -> dict[str, any]:
        """The main method to backup the Management Intents

        Returns:
            dict[str, any]: The results of the backup
        """
        try:
            self.intents_graph_data = self.make_graph_request(
                endpoint=f"{self.endpoint + self.CONFIG_ENDPOINT}/intents"
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Management Intents data from {self.endpoint + self.CONFIG_ENDPOINT}/intents: {e}",
            )
            return None
        try:
            self.template_graph_data = self.make_graph_request(
                endpoint=f"{self.endpoint + self.TEMPALETE_ENDPOINT}"
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Management Intents data from {self.endpoint + self.TEMPALETE_ENDPOINT}: {e}",
            )
            return None

        self.intent_ids = [
            {"id": intent_id["id"]} for intent_id in self.intents_graph_data["value"]
        ]
        self.assignment_responses = self.batch_assignment(
            self.intent_ids, self.assignment_endpoint, self.assignment_extra_url
        )

        intent_responses = self.batch_intents(self.intents_graph_data)

        for item in intent_responses["value"]:
            template_type = None
            base_path = self.path
            for template in self.template_graph_data["value"]:
                if item["templateId"] == template["id"]:
                    template_type = template["displayName"]

            self.path = f"{self.path}{template_type}/"

            for setting in item["settingsDelta"]:
                setting.pop("id", None)

            try:
                results = self.process_data(
                    data=item,
                    filetype=self.filetype,
                    path=self.path,
                    name_key="displayName",
                    log_message=self.LOG_MESSAGE,
                    audit_compare_info={"type": "resourceId", "value_key": "id"},
                )
                self.update_results(results)
            except Exception as e:
                self.log(
                    tag="error", msg=f"Error processing Management Intents data: {e}"
                )
                return None

            self.path = base_path

        return self.results
