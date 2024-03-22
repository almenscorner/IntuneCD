# -*- coding: utf-8 -*-
import json
import os
import re

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class EnrollmentConfigurationsUpdateModule(BaseUpdateModule):
    """A class used to update Intune Enrollment Configurations

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceEnrollmentConfigurations/"

    def __init__(self, *args, **kwargs):
        """Initializes the EnrollmentConfigurationsUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Enrollment Configurations/"
        self.assignment_endpoint = "/deviceManagement/deviceEnrollmentConfigurations/"
        self.assignment_extra_url = "/assign"
        self.exclude_paths = [
            "root['assignments']",
            "root['priority']",
            "root['deviceEnrollmentConfigurationType']",
            "root['platformType']",
        ]
        self.assignment_key = "enrollmentConfigurationAssignments"

    def _get_config_type(self, repo_data: dict[str, any]) -> str:
        """Gets the configuration type

        Args:
            repo_data (dict[str, any]): The repository data

        Returns:
            str: The configuration type
        """
        config_type = repo_data.get("deviceEnrollmentConfigurationType", None)
        config_type = config_type[0].upper() + config_type[1:]
        config_type = re.findall("[A-Z][^A-Z]*", config_type)
        config_type = " ".join(config_type)

        return config_type

    def _update_priority(
        self,
        intune_object: dict[str, any],
        repo_data_priority: str,
        config_type: str,
    ) -> None:
        """Updates the priority

        Args:
            downstream_data (list[dict[str, any]]): The Intune data
            repo_data (dict[str, any]): The repository data
            config_type (str): The configuration type
        """
        if repo_data_priority == 0:
            return None
        # get priority from intune again to check if it was updated
        intune_object = self.make_graph_request(
            self.endpoint + self.CONFIG_ENDPOINT + self.downstream_id,
        )
        intune_priority = intune_object["priority"]
        if repo_data_priority != intune_priority:
            self.log(
                msg=f"Updating Enrollment Config {config_type} Priority: " + self.name,
            )
            # Update priority
            request_data = json.dumps({"priority": repo_data_priority})
            self.make_graph_request(
                self.endpoint
                + self.CONFIG_ENDPOINT
                + self.downstream_id
                + "/setpriority",
                data=request_data,
                status_code=200,
                method="post",
            )

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

            intune_data["value"] = [
                item
                for item in intune_data["value"]
                if item["@odata.type"]
                != "#microsoft.graph.windows10EnrollmentCompletionPageConfiguration"
            ]

            for filename in os.listdir(self.path):
                self.downstream_id = None
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    if (
                        repo_data["@odata.type"]
                        == "#microsoft.graph.deviceEnrollmentPlatformRestrictionConfiguration"
                    ):
                        self.match_info = {
                            "displayName": repo_data.get("displayName"),
                            "@odata.type": repo_data.get("@odata.type"),
                            "platformType": repo_data.get("platformType"),
                        }
                    else:
                        self.match_info = {
                            "displayName": repo_data.get("displayName"),
                            "@odata.type": repo_data.get("@odata.type"),
                        }

                    self.name = repo_data.get("displayName")
                    config_type = self._get_config_type(repo_data)
                    self.config_type = f"Enrollment Configuration {config_type}"
                    repo_priority = repo_data.get("priority", None)
                    repo_data.pop("priority", None)
                    repo_data.pop("deviceEnrollmentConfigurationType", None)
                    repo_data.pop("platformType", None)
                    diff_data = self.create_diff_data(self.name, self.config_type)

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

                    if self.downstream_object:
                        self._update_priority(
                            self.downstream_object, repo_priority, config_type
                        )

                    self.set_diff_data(diff_data)
                    self.diff_summary.append(diff_data)
                    self.reset_diffs_and_count()

            for item in list(intune_data["value"]):
                # Remove items that cannot or should be removed
                if (
                    item.get("@odata.type")
                    == "#microsoft.graph.windows10EnrollmentCompletionPageConfiguration"
                    or item.get("displayName") == "All users and all devices"
                ):
                    intune_data["value"].remove(item)

            self.remove_downstream_data(self.CONFIG_ENDPOINT, intune_data["value"])

        return self.diff_summary
