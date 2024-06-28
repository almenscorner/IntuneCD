# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class EnrollmentStatusPageUpdateModule(BaseUpdateModule):
    """A class used to update Intune Enrollment Status Page

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceEnrollmentConfigurations/"
    APP_ENDPOINT = "/beta/deviceAppManagement/mobileApps"

    def __init__(self, *args, **kwargs):
        """Initializes the EnrollmentStatusPageUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Enrollment Profiles/Windows/ESP/"
        self.config_type = "Enrollment Status Page"
        self.assignment_endpoint = "/deviceManagement/deviceEnrollmentConfigurations/"
        self.assignment_extra_url = "/assign"
        self.exclude_paths = [
            "root['assignments']",
            "root['priority']",
        ]
        self.assignment_key = "enrollmentConfigurationAssignments"

    def _get_app_ids(self, repo_data: dict) -> dict[str, any]:
        """Get the app IDs for the selected apps

        Args:
            repo_data (dict): The data from the repo

        Returns:
            dict[str, any]: The updated data
        """
        if "selectedMobileAppNames" in repo_data:
            app_ids = []

            for app in repo_data["selectedMobileAppNames"]:
                param = {
                    "$filter": f"(isof('{str(app['type']).replace('#', '')}'))",
                    "$search": '"' + app["name"] + '"',
                }

                app_request = self.make_graph_request(
                    endpoint=self.endpoint + self.APP_ENDPOINT, params=param
                )
                if app_request["value"]:
                    app_ids.append(app_request["value"][0]["id"])
                else:
                    self.log(tag="warning", msg=f"App {app['name']} not found")

            if app_ids:
                repo_data.pop("selectedMobileAppNames", None)
                repo_data["selectedMobileAppIds"] = app_ids

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

                    self._get_app_ids(repo_data)
                    repo_data.pop("priority", None)

                    try:
                        self.process_update(
                            downstream_data=intune_data["value"],
                            repo_data=repo_data,
                            method="patch",
                            status_code=200,
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

            for item in list(intune_data["value"]):  # Create a copy for iteration
                # Remove items that cannot or should be removed
                if (
                    item.get("@odata.type")
                    != "#microsoft.graph.windows10EnrollmentCompletionPageConfiguration"
                    or item.get("displayName") == "All users and all devices"
                ):
                    intune_data["value"].remove(item)

            self.remove_downstream_data(self.CONFIG_ENDPOINT, intune_data["value"])

        return self.diff_summary
