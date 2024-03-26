# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class EnrollmentStatusPageBackupModule(BaseBackupModule):
    """A class used to backup Intune Enrollment Status Page

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceEnrollmentConfigurations"
    LOG_MESSAGE = "Backing up Enrollment Status Page: "
    APP_ENDPOINT = "/beta/deviceAppManagement/mobileApps"

    def __init__(self, *args, **kwargs):
        """Initializes the EnrollmentStatusPageBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Enrollment Profiles/Windows/ESP/"
        self.assignment_endpoint = "deviceManagement/deviceEnrollmentConfigurations/"
        self.assignment_extra_url = "/assignments"
        self.audit = False

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
                msg=f"Error getting Enrollment Status Page data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        # Only get the windows10EnrollmentCompletionPageConfiguration from the data
        self.graph_data = [
            item
            for item in self.graph_data["value"]
            if item["@odata.type"]
            == "#microsoft.graph.windows10EnrollmentCompletionPageConfiguration"
        ]

        for item in self.graph_data:
            # Get the app names from the app ids
            if "selectedMobileAppIds" in item:
                app_ids = item["selectedMobileAppIds"]
                app_names = []
                for app_id in app_ids:
                    app_data = self.make_graph_request(
                        endpoint=f"{self.endpoint + self.APP_ENDPOINT}/{app_id}"
                    )
                    if app_data:
                        app = {
                            "name": app_data["displayName"],
                            "type": app_data["@odata.type"],
                        }
                        app_names.append(app)
                if app_names:
                    item.pop("selectedMobileAppIds", None)
                    item["selectedMobileAppNames"] = app_names

        try:
            self.results = self.process_data(
                data=self.graph_data,
                filetype=self.filetype,
                path=self.path,
                name_key="displayName",
                log_message=self.LOG_MESSAGE,
            )
        except Exception as e:
            self.log(
                tag="error", msg=f"Error processing Enrollment Status Page data: {e}"
            )
            return None

        return self.results
