# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class WindowsEnrollmentProfileUpdateModule(BaseUpdateModule):
    """A class used to update Intune Windows Enrollment Profile

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/windowsAutopilotDeploymentProfiles/"

    def __init__(self, *args, **kwargs):
        """Initializes the WindowsEnrollmentProfileUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Enrollment Profiles/Windows/"
        self.config_type = "Windows Enrollment Profile"
        self.assignment_endpoint = (
            "/deviceManagement/windowsAutopilotDeploymentProfiles/"
        )
        self.assignment_extra_url = "/assignments"
        self.exclude_paths = [
            "root['assignments']",
        ]
        # Windows enrollment profile assginment is handled differently, so we need to set the following attributes
        self.handle_iterable_assignment = True
        self.assignment_key = "target"
        self.assignment_status_code = 201

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
                    if not repo_data.get("managementServiceAppId"):
                        repo_data["managementServiceAppId"] = ""

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

            for item in intune_data["value"]:
                if self.remove:
                    # Remvoe any assignments before removing the profile
                    endpoint = f"{self.endpoint}{self.CONFIG_ENDPOINT}{item['id']}{self.assignment_extra_url}"
                    self.make_graph_request(endpoint, method="delete", status_code=200)
            self.remove_downstream_data(self.CONFIG_ENDPOINT, intune_data["value"])

        return self.diff_summary
