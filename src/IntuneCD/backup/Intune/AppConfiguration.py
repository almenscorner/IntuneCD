# -*- coding: utf-8 -*-
import json

from ...intunecdlib.BaseBackupModule import BaseBackupModule


class AppConfigurationBackupModule(BaseBackupModule):
    """A class used to backup Intune App Configurations

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceAppManagement/mobileAppConfigurations"
    LOG_MESSAGE = "Backing up App Configuration: "
    APP_ENDPOINT = "/beta/deviceAppManagement/mobileApps"

    def __init__(self, *args, **kwargs):
        """Initializes the AppConfigurationBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/App Configuration/"
        self.audit_filter = "componentName eq 'MobileAppConfiguration'"
        self.assignment_endpoint = "deviceAppManagement/mobileAppConfigurations/"
        self.assignment_extra_url = "/assignments"

    def main(self) -> dict[str, any]:
        """The main method to backup the App Configurations

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
                msg=f"Error getting App Configuration data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        if self.graph_data["value"]:
            item = ""
            for item in self.graph_data["value"]:
                for app in item["targetedMobileApps"]:
                    app_data = self.make_graph_request(
                        endpoint=self.endpoint + self.APP_ENDPOINT + "/" + app
                    )
                    if app_data:
                        item.pop("targetedMobileApps")
                        item["targetedMobileApps"] = {}
                        item["targetedMobileApps"]["appName"] = app_data["displayName"]
                        item["targetedMobileApps"]["type"] = app_data["@odata.type"]
                if item.get("payloadJson"):
                    item["payloadJson"] = self.decode_base64(item["payloadJson"])
                    item["payloadJson"] = json.loads(item["payloadJson"])

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
            self.log(tag="error", msg=f"Error processing App Configuration data: {e}")
            return None

        return self.results
