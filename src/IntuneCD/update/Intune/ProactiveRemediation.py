# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class ProactiveRemediationUpdateModule(BaseUpdateModule):
    """A class used to update Intune Proactive Remediation

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceHealthScripts/"

    def __init__(self, *args, **kwargs):
        """Initializes the ProactiveRemediationUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Proactive Remediations/"
        self.script_data_path = f"{self.path}Script Data/"
        self.assignment_endpoint = "/deviceManagement/deviceHealthScripts/"
        self.assignment_extra_url = "/assign"
        self.assignment_key = "deviceHealthScriptAssignments"

    def _get_script_data(self, filename: str) -> tuple[str, str]:
        fname_id = filename.split("__")
        detection_script_name = ""
        remediation_script_name = ""

        if len(fname_id) > 1:
            fname_id = fname_id[1].replace(".json", "").replace(".yaml", "")
        else:
            fname_id = ""

        # Get all remediation scripts and detection scripts files
        script_files = os.listdir(self.script_data_path)

        # Filter out files that matches the id
        script_files = [f for f in script_files if fname_id in f]

        # Set detection and remediation script name and path
        for f in script_files:
            if "detectionscript" in f.lower():
                detection_script_name = f"{self.script_data_path}{f}"
            elif "remediationscript" in f.lower():
                remediation_script_name = f"{self.script_data_path}{f}"

        if detection_script_name and remediation_script_name:
            detection_script = self.load_script_file(detection_script_name)
            remediation_script = self.load_script_file(remediation_script_name)
            return detection_script, remediation_script

        return "", ""

    def _handle_script_diff(
        self, repo_script: str, intune_script: str, repo_data: dict[str, any]
    ) -> None:
        """Handle the script diff

        Args:
            script (str): The script to handle
        """
        diff = self.get_diffs(repo_script, intune_script)

        if diff:
            self.update_downstream_data(
                config_endpoint=self.endpoint
                + self.CONFIG_ENDPOINT
                + self.downstream_id,
                method="patch",
                data=repo_data,
                status_code=200,
            )

            self.update_diff_data(diff)

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

            profile_ids = [profile["id"] for profile in intune_data["value"]]

            remediation_data = self.batch_request(
                profile_ids,
                "deviceManagement/deviceHealthScripts/",
                "",
            )

            for filename in os.listdir(self.path):
                self.config_type = "Proactive Remediation"
                self.notify = True
                self.exclude_paths = [
                    "root['assignments']",
                    "root['detectionScriptContent']",
                    "root['remediationScriptContent']",
                    "root['deviceHealthScriptType']",
                ]

                repo_data = self.load_repo_data(filename)
                if repo_data:
                    repo_data.pop("deviceHealthScriptType", None)
                    self.match_info = {
                        "displayName": repo_data.get("displayName"),
                    }
                    self.name = repo_data.get("displayName")
                    diff_data = self.create_diff_data(self.name, self.config_type)
                    (
                        repo_detection_script,
                        repo_remediation_script,
                    ) = self._get_script_data(filename)

                    repo_data["detectionScriptContent"] = self.encode_base64(
                        repo_detection_script
                    )
                    repo_data["remediationScriptContent"] = self.encode_base64(
                        repo_remediation_script
                    )

                    try:
                        self.process_update(
                            downstream_data=remediation_data,
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
                        self.notify = False
                        intune_detection_script = self.decode_base64(
                            self.downstream_object.get("detectionScriptContent")
                        )
                        intune_remediation_script = self.decode_base64(
                            self.downstream_object.get("remediationScriptContent")
                        )
                        self.config_type = "Detection Script"
                        self.message = (
                            "Detection Script changed, check commit history for details"
                        )
                        self.exclude_paths = [
                            "root['assignments']",
                            "root['remediationScriptContent']",
                        ]
                        self._handle_script_diff(
                            repo_detection_script, intune_detection_script, repo_data
                        )

                        self.config_type = "Remediation Script"
                        self.message = "Remediation Script changed, check commit history for details"
                        self.exclude_paths = [
                            "root['assignments']",
                            "root['detectionScriptContent']",
                        ]
                        self._handle_script_diff(
                            repo_remediation_script,
                            intune_remediation_script,
                            repo_data,
                        )

                    self.set_diff_data(diff_data)
                    self.diff_summary.append(diff_data)
                    self.reset_diffs_and_count()

            for item in list(remediation_data):
                if item.get("publisher") == "Microsoft":
                    remediation_data.remove(item)
            self.remove_downstream_data(self.CONFIG_ENDPOINT, remediation_data)

        return self.diff_summary
