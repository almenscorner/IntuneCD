# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class AppProtectionUpdateModule(BaseUpdateModule):
    """A class used to update Intune App Protections

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
    """

    CONFIG_ENDPOINT = "/beta/deviceAppManagement/"

    def __init__(self, *args, **kwargs):
        """Initializes the AppProtectionUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/App Protection/"
        self.config_type = "App Protection"
        self.assignment_endpoint = "/deviceAppManagement/"
        self.assignment_extra_url = "/assign"
        self.exclude_paths = [
            "root['displayName']",
            "root['assignments']",
        ]
        self.app_protection = True
        self.assignment_status_code = 204
        self.remove_status_code = 204

    def _get_platform(self, repo_data: dict) -> str:
        """Gets the platform of the App Protection

        Args:
            repo_data (dict): The data of the App Protection

        Returns:
            str: The platform of the App Protection
        """
        if (
            repo_data["@odata.type"]
            == "#microsoft.graph.mdmWindowsInformationProtectionPolicy"
        ):
            platform = "mdmWindowsInformationProtectionPolicies"
        elif (
            repo_data["@odata.type"]
            == "#microsoft.graph.windowsInformationProtectionPolicy"
        ):
            platform = "windowsInformationProtectionPolicies"
        else:
            platform = f"{str(repo_data['@odata.type']).split('.')[2]}s"

        return platform

    def _get_match_info(self, repo_data: dict) -> dict[str, any]:
        """Gets the match info of the App Protection

        Args:
            repo_data (dict): The data of the App Protection

        Returns:
            dict[str, any]: The match info of the App Protection
        """
        if (
            "targetedAppManagementLevels" in repo_data
            and repo_data["targetedAppManagementLevels"] != "unspecified"
        ):
            match_info = {
                "displayName": repo_data.get("displayName"),
                "targetedAppManagementLevels": repo_data.get(
                    "targetedAppManagementLevels"
                ),
            }
        else:
            match_info = {
                "displayName": repo_data.get("displayName"),
                "@odata.type": repo_data.get("@odata.type"),
            }

        return match_info

    def main(self) -> dict[str, any]:
        """The main method to update the Intune data"""
        if self.path_exists():
            try:
                intune_data = self.get_downstream_data(
                    self.CONFIG_ENDPOINT + "managedAppPolicies"
                )
            except Exception as e:
                self.log(tag="error", msg=f"Error getting {self.config_type} data: {e}")
                return None

            self.downstream_assignments = self.batch_assignment(
                intune_data["value"],
                self.assignment_endpoint,
                "/assignments",
            )

            for filename in os.listdir(self.path):
                self.assignment_endpoint = "/deviceAppManagement/"
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    self.match_info = self._get_match_info(repo_data)
                    self.name = repo_data.get("displayName")
                    diff_data = self.create_diff_data(self.name, self.config_type)
                    if (
                        repo_data["@odata.type"]
                        == "#microsoft.graph.windowsInformationProtectionPolicy"
                    ):
                        status_code = 200
                    else:
                        status_code = 204

                    # Get the platform of the App Protection
                    platform = self._get_platform(repo_data)

                    self.assignment_endpoint = f"{self.assignment_endpoint}{platform}/"
                    config_endpoint = f"{self.CONFIG_ENDPOINT}{platform}/"

                    try:
                        self.process_update(
                            downstream_data=intune_data["value"],
                            repo_data=repo_data,
                            method="patch",
                            status_code=status_code,
                            config_endpoint=config_endpoint,
                        )
                    except Exception as e:
                        self.log(
                            tag="error",
                            msg=f"Error updating {self.config_type} {self.name}: {e}",
                        )

                    self.set_diff_data(diff_data)
                    self.diff_summary.append(diff_data)
                    self.reset_diffs_and_count()

            self.remove_downstream_data(
                self.CONFIG_ENDPOINT + "managedAppPolicies/", intune_data["value"]
            )

        return self.diff_summary
