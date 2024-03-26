# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class WindowsFeatureUpdatesUpdateModule(BaseUpdateModule):
    """A class used to update Intune Windows Feature Updates

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/windowsFeatureUpdateProfiles/"

    def __init__(self, *args, **kwargs):
        """Initializes the WindowsFeatureUpdatesUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Feature Updates/"
        self.config_type = "Windows Feature Update"
        self.assignment_endpoint = "/deviceManagement/windowsFeatureUpdateProfiles/"
        self.assignment_extra_url = "/assign"
        self.exclude_paths = [
            "root['assignments']",
            "root['deployableContentDisplayName']",
            "root['endOfSupportDate']",
            "root['installLatestWindows10OnWindows11IneligibleDevice']",
        ]

    def main(self) -> dict[str, any]:
        """The main method to update the Intune data"""
        if self.path_exists():
            try:
                intune_data = self.get_downstream_data(self.CONFIG_ENDPOINT)
            except Exception as e:
                self.log(tag="error", msg=f"Error getting {self.config_type} data: {e}")
                return None

            self.downstream_assignments = self.batch_assignment(
                intune_data["value"],
                self.assignment_endpoint,
                "/assignments",
            )

            for filename in os.listdir(self.path):
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    self.match_info = {
                        "displayName": repo_data.get("displayName"),
                    }
                    self.name = repo_data.get("displayName")
                    diff_data = self.create_diff_data(self.name, self.config_type)
                    create_data = repo_data.copy()
                    self.get_pop_keys(
                        repo_data,
                        [
                            "deployableContentDisplayName",
                            "endOfSupportDate",
                            "installLatestWindows10OnWindows11IneligibleDevice",
                        ],
                        "pop",
                    )

                    try:
                        self.process_update(
                            downstream_data=intune_data["value"],
                            repo_data=repo_data,
                            method="patch",
                            status_code=200,
                            config_endpoint=self.CONFIG_ENDPOINT,
                            create_data=create_data,
                        )
                    except Exception as e:
                        self.log(
                            tag="error",
                            msg=f"Error updating {self.config_type} {self.name}: {e}",
                        )

                    self.set_diff_data(diff_data)
                    self.diff_summary.append(diff_data)
                    self.reset_diffs_and_count()

            self.remove_downstream_data(self.CONFIG_ENDPOINT, intune_data["value"])

        return self.diff_summary
