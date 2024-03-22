# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class ReusableSettingsUpdateModule(BaseUpdateModule):
    """A class used to update Intune Reusable Settings

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/reusablePolicySettings/"

    def __init__(self, *args, **kwargs):
        """Initializes the TemplateUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Compliance Policies/Scripts/"
        self.config_type = "Compliance Script Policy"
        self.params = {
            "$select": "id,settinginstance,displayname,description,settingDefinitionId,version"
        }
        self.exclude_paths = [
            "root['displayName']",
            "root['assignments']",
            "root['settingInstance']['simpleSettingValue']['value']",
        ]
        self.handle_assignment = False

    def _script_diff_check(
        self,
        repo_data: dict,
    ) -> None:
        self.message = "Script changed, check commit history for details"
        script_diff = self.get_diffs(
            repo_data["settingInstance"]["simpleSettingValue"]["value"],
            self.downstream_object["settingInstance"]["simpleSettingValue"]["value"],
        )

        if script_diff:
            self.update_downstream_data(
                self.endpoint + self.CONFIG_ENDPOINT + self.downstream_id,
                "put",
                204,
                repo_data,
            )

            self.diff_summary.append(script_diff)

    def main(self) -> dict[str, any]:
        """The main method to update the Intune data"""
        if self.path_exists():
            try:
                intune_data = self.get_downstream_data(self.CONFIG_ENDPOINT)
            except Exception as e:
                self.log(tag="error", msg=f"Error getting {self.config_type} data: {e}")
                return None

            for filename in os.listdir(self.path):
                self.notify = True
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    # If policy does not contain settingDefinitionId skip as it is not a reusable setting
                    if not repo_data.get("settingDefinitionId"):
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
                            method="put",
                            status_code=204,
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
