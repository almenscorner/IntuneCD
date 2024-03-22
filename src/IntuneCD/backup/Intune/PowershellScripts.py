# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseBackupModule import BaseBackupModule


class PowershellScriptsBackupModule(BaseBackupModule):
    """A class used to backup Intune Powershell Scripts

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceManagementScripts/"
    LOG_MESSAGE = "Backing up Powershell Script: "

    def __init__(self, *args, **kwargs):
        """Initializes the PowershellScriptsBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Scripts/Powershell/"
        self.script_data_path = f"{self.path}/Script Data/"
        self.audit_filter = (
            self.audit_filter or "componentName eq 'DeviceConfiguration'"
        )
        self.assignment_endpoint = "deviceManagement/deviceManagementScripts/"
        self.assignment_extra_url = "/assignments"

    def _save_script(self, item: dict) -> None:
        """Saves the script to a file

        Args:
            item (dict): The script data
        """
        if self.prefix:
            match = self.check_prefix_match(item["displayName"], self.prefix)
            if not match:
                return
        script_name = self._prepare_file_name(item["fileName"].replace(".ps1", ""))
        if self.append_id:
            script_name = f"{script_name}__{item['id']}"
        if item.get("scriptContent"):
            try:
                if not os.path.exists(self.script_data_path):
                    os.makedirs(self.script_data_path)
            except Exception as e:
                self.log(
                    tag="error",
                    msg=f"Error creating directory {self.script_data_path}: {e}",
                )
            decoded = self.decode_base64(item["scriptContent"])
            try:
                with open(
                    f"{self.script_data_path}{script_name}.ps1",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(decoded)
            except Exception as e:
                self.log(
                    tag="error", msg=f"Error writing script {script_name} to file: {e}"
                )

    def main(self) -> dict[str, any]:
        """The main method to backup the Powershell Scripts

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
                msg=f"Error getting Powershell Script data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        script_ids = [item["id"] for item in self.graph_data["value"]]
        # Get the script data details using batch request
        script_responses = self.batch_request(
            script_ids, "deviceManagement/deviceManagementScripts/", ""
        )

        # Save the script data to file
        for item in script_responses:
            self._save_script(item)

        try:
            self.results = self.process_data(
                data=script_responses,
                filetype=self.filetype,
                path=self.path,
                name_key="displayName",
                log_message=self.LOG_MESSAGE,
                audit_compare_info={"type": "resourceId", "value_key": "id"},
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing Powershell Script data: {e}")
            return None

        return self.results
