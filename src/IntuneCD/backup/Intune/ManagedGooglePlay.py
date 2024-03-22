# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class ManagedGooglePlayBackupModule(BaseBackupModule):
    """A class used to backup Intune Managed Google Play

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = (
        "/beta/deviceManagement/androidManagedStoreAccountEnterpriseSettings"
    )
    LOG_MESSAGE = "Backing up Managed Google Play: "

    def __init__(self, *args, **kwargs):
        """Initializes the ManagedGooglePlayBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Managed Google Play/"
        self.audit_filter = self.audit_filter or (
            "resources/any(s:s/auditResourceType eq "
            "'Microsoft.Management.Services.Api.AndroidManagedStoreAccountEnterpriseSettings')"
        )
        # Managed Google Play has no assignments, so exclude assignments from the run
        self.has_assignments = False

    def main(self) -> dict[str, any]:
        """The main method to backup the Managed Google Play

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
                msg=f"Error getting Managed Google Play data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        try:
            self.results = self.process_data(
                data=self.graph_data,
                filetype=self.filetype,
                path=self.path,
                name_key="ownerUserPrincipalName",
                log_message=self.LOG_MESSAGE,
                audit_compare_info={
                    "type": "auditResourceType",
                    "value_key": "Microsoft.Management.Services.Api.AndroidManagedStoreAccountEnterpriseSettings",
                },
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing Managed Google Play data: {e}")
            return None

        return self.results
