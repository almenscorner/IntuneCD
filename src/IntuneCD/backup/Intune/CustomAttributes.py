# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseBackupModule import BaseBackupModule


class CustomAttributesBackupModule(BaseBackupModule):
    """A class used to backup Intune Custom Attributes

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceCustomAttributeShellScripts/"
    LOG_MESSAGE = "Backing up Custom Attribute: "

    def __init__(self, *args, **kwargs):
        """Initializes the CustomAttributesBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Custom Attributes/"
        self.script_data_path = f"{self.path}/Script Data/"
        self.audit_filter = (
            self.audit_filter or "componentName eq 'DeviceConfiguration'"
        )
        self.assignment_endpoint = "deviceManagement/deviceCustomAttributeShellScripts/"
        self.assignment_extra_url = "?$expand=assignments"

    def _save_script(self, item: dict) -> None:
        """Saves the script to a file

        Args:
            item (dict): The item to save the script for
        """
        if self.prefix:
            match = self.check_prefix_match(item["displayName"], self.prefix)
            if not match:
                return
        script_name = self._prepare_file_name(item["fileName"].replace(".sh", ""))
        if self.append_id:
            script_name = f"{script_name}__{item['id']}"
        if item.get("scriptContent"):
            try:
                if not os.path.exists(self.script_data_path):
                    os.makedirs(self.script_data_path)
            except Exception as e:
                self.log(tag="error", msg=f"Error creating script data path: {e}")
                return None

            decoded = self.decode_base64(item["scriptContent"])

            try:
                with open(
                    f"{self.script_data_path}{script_name}.sh",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(decoded)
            except Exception as e:
                self.log(tag="error", msg=f"Error writing script data to file: {e}")
                return None

    def main(self) -> dict[str, any]:
        """The main method to backup the Custom Attributes

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
                msg=f"Error getting Custom Attribute data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        script_ids = [item["id"] for item in self.graph_data["value"]]
        # Get script data details using batch request
        script_responses = self.batch_request(
            script_ids, "deviceManagement/deviceCustomAttributeShellScripts/", ""
        )

        # Save the script data to a file
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
            self.log(tag="error", msg=f"Error processing Custom Attribute data: {e}")
            return None

        return self.results
