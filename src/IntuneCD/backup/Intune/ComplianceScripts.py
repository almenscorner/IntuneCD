# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseBackupModule import BaseBackupModule


class ComplianceScriptsBackupModule(BaseBackupModule):
    """A class used to backup Intune Compliance Scripts

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceComplianceScripts/"
    LOG_MESSAGE = "Backing up Compliance Script: "

    def __init__(self, *args, **kwargs):
        """Initializes the ComplianceScriptsBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Compliance Policies/Scripts/"
        self.script_data_path = f"{self.path}/Script Data/"
        self.audit_filter = (
            self.audit_filter or "componentName eq 'DeviceConfiguration'"
        )
        # Compliance Scripts has no assignments, so exclude assignments from the run
        self.has_assignments = False

    def _save_script(self, item: dict) -> None:
        # If there is a detectionScriptContent, get the name of the script and write the content to a file
        if self.prefix:
            match = self.check_prefix_match(item["displayName"], self.prefix)
            if not match:
                return
        if item.get("detectionScriptContent"):
            if self.append_id:
                script_name = (
                    f"{item['displayName'].replace('.ps1', '')}__{item['id']}.ps1"
                )
            else:
                script_name = f"{item['displayName'].replace('.ps1', '')}.ps1"
            if not os.path.exists(self.script_data_path):
                os.makedirs(self.script_data_path)
            decoded = self.decode_base64(item["detectionScriptContent"])
            f = open(
                f"{self.script_data_path}{script_name}",
                "w",
                encoding="utf-8",
            )
            f.write(decoded)

    def main(self) -> dict[str, any]:
        """The main method to backup the Compliance Scripts

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
                msg=f"Error getting Compliance Script data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        script_ids = [script["id"] for script in self.graph_data["value"]]

        # Get script data details using batch request
        script_data_responses = self.batch_request(
            script_ids, "deviceManagement/deviceComplianceScripts/", ""
        )

        for item in script_data_responses:
            self._save_script(item)

        try:
            self.results = self.process_data(
                data=script_data_responses,
                filetype=self.filetype,
                path=self.path,
                name_key="displayName",
                log_message=self.LOG_MESSAGE,
                audit_compare_info={"type": "resourceId", "value_key": "id"},
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing Compliance Script data: {e}")
            return None

        return self.results
