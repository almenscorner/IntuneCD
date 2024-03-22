# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseBackupModule import BaseBackupModule


class ProactiveRemediationScriptBackupModule(BaseBackupModule):
    """A class used to backup Intune Proactive Remediation Scripts

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceHealthScripts"
    LOG_MESSAGE = "Backing up Proactive Remediation: "

    def __init__(self, *args, **kwargs):
        """Initializes the ProactiveRemediationScriptBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Proactive Remediations/"
        self.script_data_path = f"{self.path}/Script Data/"
        self.audit_filter = (
            self.audit_filter or "componentName eq 'DeviceConfiguration'"
        )
        self.assignment_endpoint = "deviceManagement/deviceHealthScripts/"
        self.assignment_extra_url = "/assignments"

    def _save_script(self, item: dict, script_type: str) -> None:
        """Saves the script to a file

        Args:
            item (dict): The script data
            script_type (str): The type of script to save
        """
        if self.prefix:
            match = self.check_prefix_match(item["displayName"], self.prefix)
            if not match:
                return
        try:
            if not os.path.exists(self.script_data_path):
                os.makedirs(self.script_data_path)
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error creating directory {self.script_data_path}: {e}",
            )

        # Save detection script to the Script Data folder
        fname = self._prepare_file_name(item["displayName"])
        if self.append_id:
            fname_id = f"__{item['id']}"
        else:
            fname_id = ""
        decoded = self.decode_base64(item[f"{script_type}Content"])
        try:
            with open(
                f"{self.script_data_path}{fname}_{script_type}{fname_id}.ps1",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(decoded)
        except Exception as e:
            self.log(tag="error", msg=f"Error writing script {fname} to file: {e}")

    def main(self) -> dict[str, any]:
        """The main method to backup the Proactive Remediation Scripts

        Returns:
            dict[str, any]: The results of the backup
        """
        try:
            self.graph_data = self.make_graph_request(
                endpoint=self.endpoint + self.CONFIG_ENDPOINT
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Proactive Remediation data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        proactiveremediation_ids = [item["id"] for item in self.graph_data["value"]]
        # Get the script data details using batch request
        proactiveremediations_responses = self.batch_request(
            proactiveremediation_ids, "deviceManagement/deviceHealthScripts/", ""
        )
        # Get items that are not from Microsoft
        proactiveremediations_responses = [
            item
            for item in proactiveremediations_responses
            if "Microsoft" not in item["publisher"]
        ]

        # Save the script data to file
        for item in proactiveremediations_responses:
            self._save_script(item, "detectionScript")
            self._save_script(item, "remediationScript")

        try:
            self.results = self.process_data(
                data=proactiveremediations_responses,
                filetype=self.filetype,
                path=self.path,
                name_key="displayName",
                log_message=self.LOG_MESSAGE,
                audit_compare_info={"type": "resourceId", "value_key": "id"},
            )
        except Exception as e:
            self.log(
                tag="error", msg=f"Error processing Proactive Remediation data: {e}"
            )
            return None

        return self.results
