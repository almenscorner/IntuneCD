# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class APNSBackupModule(BaseBackupModule):
    """A class used to backup Intune Apple Push Notifications

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/applePushNotificationCertificate"
    LOG_MESSAGE = "Backing up Apple Push Notification: "

    def __init__(self, *args, **kwargs):
        """Initializes the APNSBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Apple Push Notification/"
        self.append_id = False
        self.audit_filter = self.audit_filter or (
            "resources/any(s:s/auditResourceType "
            "eq 'Microsoft.Management.Services.Api.ApplePushNotificationCertificate')"
        )
        # APNs has no assignments, so exclude assignments from the run
        self.has_assignments = False

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
                msg=f"Error getting APNs data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        try:
            self.results = self.process_data(
                data=self.graph_data,
                filetype=self.filetype,
                path=self.path,
                name_key="appleIdentifier",
                log_message=self.LOG_MESSAGE,
                audit_compare_info={
                    "type": "auditResourceType",
                    "value_key": "Microsoft.Management.Services.Api.ApplePushNotificationCertificate",
                },
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing APNs data: {e}")
            return None

        return self.results
