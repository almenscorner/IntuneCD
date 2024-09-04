# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class SettingsCatalogUpdateModule(BaseUpdateModule):
    """A class used to update Intune

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/configurationPolicies/"

    def __init__(self, *args, **kwargs):
        """Initializes the SettingsCatalogUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Settings Catalog/"
        self.config_type = "Settings Catalog"
        self.assignment_endpoint = "/deviceManagement/configurationPolicies/"
        self.assignment_extra_url = "/assign"
        self.exclude_paths = [
            "root['assignments']",
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

            profile_ids = [x["id"] for x in intune_data["value"]]
            batch_data = self.batch_request(
                profile_ids, "deviceManagement/configurationPolicies/", ""
            )
            batch_settings = self.batch_request(
                profile_ids,
                "deviceManagement/configurationPolicies/",
                "/settings?&top=1000",
            )

            for profile in batch_data:
                settings = self.get_object_details(profile["id"], batch_settings)
                if settings:
                    profile["settings"] = settings

            for filename in os.listdir(self.path):
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    if (
                        "templateReference" in repo_data
                        and repo_data["templateReference"].get("templateDisplayName")
                        == "Endpoint detection and response"
                    ):
                        self.log(
                            msg=f'Skipping "{repo_data["name"]}", Endpoint detection and response is currently not supported...',
                        )
                        continue
                    self.match_info = {
                        "name": repo_data.get("name"),
                        "technologies": repo_data.get("technologies"),
                    }
                    self.name = repo_data.get("name")
                    diff_data = self.create_diff_data(self.name, self.config_type)

                    try:
                        self.process_update(
                            downstream_data=batch_data,
                            repo_data=repo_data,
                            method="put",
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

            self.remove_downstream_data(self.CONFIG_ENDPOINT, batch_data)

        return self.diff_summary
