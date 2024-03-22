# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class NotificationTemplateBackupModule(BaseBackupModule):
    """A class used to backup Intune Notification Templates

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/notificationMessageTemplates"
    LOG_MESSAGE = "Backing up Notification Message Template: "

    def __init__(self, *args, **kwargs):
        """Initializes the NotificationTemplateBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Compliance Policies/Message Templates/"
        self.audit_filter = (
            self.audit_filter or "componentName eq 'NotificationMessageTemplate'"
        )
        # Notification Templates has no assignments, so exclude assignments from the run
        self.has_assignments = False

    def main(self) -> dict[str, any]:
        """The main method to backup the Notification Templates

        Returns:
            dict[str, any]: The results of the backup
        """
        try:
            self.graph_data = self.make_graph_request(
                endpoint=self.endpoint + self.CONFIG_ENDPOINT,
                params="?$expand=localizedNotificationMessages",
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Notification Template data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        self.graph_data = [
            item
            for item in self.graph_data["value"]
            if item.get("displayName") != "EnrollmentNotificationInternalMEO"
        ]

        # Remove the keys that are not needed
        for item in self.graph_data:
            for locale in item.get("localizedNotificationMessages"):
                self.remove_keys(locale)

        try:
            self.results = self.process_data(
                data=self.graph_data,
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
            self.log(
                tag="error", msg=f"Error processing Notification Template data: {e}"
            )
            return None

        return self.results
