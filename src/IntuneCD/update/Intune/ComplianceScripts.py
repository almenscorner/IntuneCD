# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class ComplianceScriptsUpdateModule(BaseUpdateModule):
    """A class used to update Intune Compliance Scripts

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceComplianceScripts/"

    def __init__(self, *args, **kwargs):
        """Initializes the ComplianceScriptsUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Compliance Policies/Scripts/"
        self.config_type = "Compliance Script Policy"
        self.handle_assignment = False
        self.exclude_paths = "root['detectionScriptContent']"

    def _script_diff_check(self, repo_data: dict) -> None:
        script_diff = self.get_diffs(
            repo_data["detectionScriptContent"],
            self.downstream_object["detectionScriptContent"],
        )

        if script_diff:
            self.message = "Script changed, check commit history for details"
            self.update_downstream_data(
                self.endpoint + self.CONFIG_ENDPOINT + self.downstream_id,
                "patch",
                200,
                repo_data,
            )

            self.update_diff_data(script_diff)

    def _get_script_details(self, intune_data: dict) -> dict[str, any]:
        new_intune_data = []
        for item in intune_data["value"]:
            script_data = self.make_graph_request(
                self.endpoint + self.CONFIG_ENDPOINT + item["id"]
            )

            if script_data:
                item.clear()
                item.update(script_data)
                new_intune_data.append(item)

        return new_intune_data

    def main(self) -> dict[str, any]:
        """The main method to update the Intune data"""
        if self.path_exists():
            try:
                intune_data = self.get_downstream_data(self.CONFIG_ENDPOINT)
            except Exception as e:
                self.log(tag="error", msg=f"Error getting {self.config_type}: {e}")
                return None
            # Get details for each script to populate script content
            intune_data["value"] = self._get_script_details(intune_data)
            for filename in os.listdir(self.path):
                self.notify = True
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    # Skip if policy contains settingDefinitionId as it is not a device compliance script
                    if repo_data.get("settingDefinitionId"):
                        continue
                    self.match_info = {
                        "displayName": repo_data.get("displayName"),
                    }

                    self.name = repo_data.get("displayName")
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

                    # Check for diff on script
                    if self.downstream_object:
                        self.notify = False
                        self._script_diff_check(repo_data)

                    self.set_diff_data(diff_data)
                    self.diff_summary.append(diff_data)
                    self.reset_diffs_and_count()

            self.remove_downstream_data(self.CONFIG_ENDPOINT, intune_data["value"])

        return self.diff_summary
