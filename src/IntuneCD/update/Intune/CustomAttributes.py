# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class CustomAttributesUpdateModule(BaseUpdateModule):
    """A class used to update Intune Custom Attributes

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceCustomAttributeShellScripts/"

    def __init__(self, *args, **kwargs):
        """Initializes the CustomAttributesUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Custom Attributes/"
        self.script_data_path = f"{self.path}Script Data/"
        self.config_type = "Custom Attribute"
        self.assignment_endpoint = "/deviceManagement/deviceManagementScripts/"
        self.assignment_extra_url = "/assign"
        self.exclude_paths = [
            "root['assignments']",
            "root['scriptContent']",
            "root['customAttributeName']",
            "root['customAttributeType']",
            "root['displayName']",
        ]
        self.assignment_key = "deviceManagementScriptAssignments"

    def _get_script_file(self, filename: str, repo_data: dict[str, any]) -> str:
        """Gets the script file

        Args:
            filename (str): The filename to get the script file for
            repo_data (dict[str, any]): The repository data

        Returns:
            str: The script file
        """
        fname_id = filename.split("__")
        if len(fname_id) > 1:
            fname_id = fname_id[1].replace(".json", "").replace(".yaml", "")
        else:
            fname_id = None
        script_files = os.listdir(self.script_data_path)

        if not fname_id:
            script_file = [x for x in script_files if repo_data["fileName"] in x]
        else:
            script_file = [x for x in script_files if fname_id in x]

        if len(script_file) == 1:
            return script_file[0]

        return None

    def _handle_script_diffs(
        self, repo_script: str, intune_script: str, repo_data: dict[str, any]
    ):
        self.message = "Script changed, check commit history for details"
        script_diff = self.get_diffs(repo_script, intune_script, None)

        if script_diff:
            repo_data.pop("assignments", None)
            self.update_downstream_data(
                self.endpoint + self.CONFIG_ENDPOINT + self.downstream_id,
                "patch",
                200,
                repo_data,
            )

            self.update_diff_data(script_diff)

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
                "deviceManagement/deviceCustomAttributeShellScripts/",
                "?$expand=assignments",
            )

            profile_ids = [profile["id"] for profile in intune_data["value"]]

            shell_script_data = self.batch_request(
                profile_ids,
                "deviceManagement/deviceCustomAttributeShellScripts/",
                "",
            )

            for filename in os.listdir(self.path):
                self.notify = True
                script_data = None
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    self.match_info = {
                        "displayName": repo_data.get("displayName"),
                    }
                    self.name = repo_data.get("displayName")
                    diff_data = self.create_diff_data(self.name, self.config_type)

                    script_file = self._get_script_file(filename, repo_data)
                    if script_file:
                        script_data = self.load_script_file(
                            self.script_data_path + script_file
                        )
                        repo_data["scriptContent"] = self.encode_base64(script_data)

                    update_data = repo_data.copy()
                    self.get_pop_keys(
                        update_data,
                        ["customAttributeName", "customAttributeType", "displayName"],
                        "pop",
                    )

                    try:
                        self.process_update(
                            downstream_data=shell_script_data,
                            repo_data=repo_data,
                            method="patch",
                            status_code=200,
                            config_endpoint=self.CONFIG_ENDPOINT,
                            update_data=update_data,
                        )
                    except Exception as e:
                        self.log(
                            tag="error",
                            msg=f"Error updating {self.config_type} {self.name}: {e}",
                        )

                    if self.downstream_object:
                        self.notify = False
                        if script_data:
                            intune_script_data = self.decode_base64(
                                self.downstream_object["scriptContent"]
                            )
                            self._handle_script_diffs(
                                script_data,
                                intune_script_data,
                                update_data,
                            )

                    self.set_diff_data(diff_data)
                    self.diff_summary.append(diff_data)
                    self.reset_diffs_and_count()

            self.remove_downstream_data(self.CONFIG_ENDPOINT, shell_script_data)

        return self.diff_summary
