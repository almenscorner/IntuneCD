# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class AppConfigurationUpdateModule(BaseUpdateModule):
    """A class used to update Intune App Configurations

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceAppManagement/mobileAppConfigurations/"
    APP_ENDPOINT = "/beta/deviceAppManagement/mobileApps"

    def __init__(self, *args, **kwargs):
        """Initializes the AppConfigurationUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/App Configuration/"
        self.config_type = "App Configuration"
        self.assignment_endpoint = "/deviceAppManagement/mobileAppConfigurations/"
        self.assignment_extra_url = (
            "/microsoft.graph.managedDeviceMobileAppConfiguration/assign"
        )
        self.exclude_paths = [
            "root['targetedMobileApps']",
            "root['assignments']",
        ]

    def _get_app_ids(self, repo_data: dict) -> dict[str, any]:
        """Gets the app IDs of the App Configuration

        Args:
            repo_data (dict): The data of the App Configuration
        """
        app_ids = {}
        # If backup contains targeted apps, search for the app
        if repo_data["targetedMobileApps"]:
            q_param = {
                "$filter": "(isof("
                + "'"
                + str(repo_data["targetedMobileApps"]["type"]).replace("#", "")
                + "'"
                + "))",
                "$search": f'"{repo_data["targetedMobileApps"]["appName"]}"',
            }
            app_request = self.make_graph_request(
                endpoint=self.endpoint + self.APP_ENDPOINT, params=q_param
            )
            if app_request["value"]:
                app_ids = app_request["value"][0]["id"]
            if app_ids:
                repo_data.pop("targetedMobileApps")
                repo_data["targetedMobileApps"] = [app_ids]
            else:
                self.log(
                    tag="warning",
                    msg=f"App {repo_data['targetedMobileApps']['appName']} not found, skipping {self.config_type} {self.name} update.",
                )

                return None

        return repo_data

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
                        "@odata.type": repo_data.get("@odata.type"),
                    }
                    self.name = repo_data.get("displayName")
                    diff_data = self.create_diff_data(self.name, self.config_type)

                    repo_data = self._get_app_ids(repo_data)
                    if repo_data is None:
                        continue

                    try:
                        self.process_update(
                            downstream_data=intune_data["value"],
                            repo_data=repo_data,
                            method="patch",
                            status_code=204,
                            config_endpoint=self.CONFIG_ENDPOINT,
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
