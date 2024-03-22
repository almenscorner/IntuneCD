# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class AppleEnrollmentProfilesBackupModule(BaseBackupModule):
    """A class used to backup Intune Apple Enrollment Profiles

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/depOnboardingSettings/"
    LOG_MESSAGE = "Backing up Apple Enrollment Profile: "

    def __init__(self, *args, **kwargs):
        """Initializes the AppleEnrollmentProfilesBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Enrollment Profiles/Apple/"
        self.audit_filter = "componentName eq 'Enrollment'"
        # Apple Enrollment Profiles has no assignments, so exclude assignments from the run
        self.has_assignments = False

    def main(self) -> dict[str, any]:
        """The main method to backup the Apple Enrollment Profiles

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
                msg=f"Error getting Apple Enrollment Profile data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        items_ids = [item["id"] for item in self.graph_data["value"]]

        # get the details of each profile using batch request
        batch_profile_data = self.batch_request(
            items_ids,
            "deviceManagement/depOnboardingSettings/",
            "/enrollmentProfiles",
        )

        # get a list of the value key from the batch_profile_data
        data = [
            value
            for profile in batch_profile_data
            for value in profile["value"]
            if value is not None
        ]

        try:
            self.results = self.process_data(
                data=data,
                filetype=self.filetype,
                path=self.path,
                name_key="displayName",
                log_message=self.LOG_MESSAGE,
                audit_compare_info={"type": "resourceId", "value_key": "id"},
            )
        except Exception as e:
            self.log(
                tag="error", msg=f"Error processing Apple Enrollment Profile data: {e}"
            )
            return None

        return self.results
