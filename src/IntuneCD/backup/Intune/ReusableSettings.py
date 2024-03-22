# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseBackupModule import BaseBackupModule


class ReusableSettingsBackupModule(BaseBackupModule):
    """A class used to backup Intune Reusable Policy Settings

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/reusablePolicySettings/"
    LOG_MESSAGE = "Backing up Reusable Policy Setting: "

    def __init__(self, *args, **kwargs):
        """Initializes the ReusableSettingsBackupModule class

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
        # Reusable Policy Settings have no assignments, so exclude assignments from the run
        self.has_assignments = False

    def _save_script(self, item: dict) -> None:
        if self.prefix:
            match = self.check_prefix_match(item["displayName"], self.prefix)
            if not match:
                return
        if self.append_id:
            script_name = f"{item['displayName'].replace('.sh', '')}__{item['id']}.sh"
        else:
            script_name = f"{item['displayName'].replace('.sh', '')}.sh"
        try:
            if not os.path.exists(self.script_data_path):
                os.makedirs(self.script_data_path)
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error creating directory {self.script_data_path}: {e}",
            )

        decoded = self.decode_base64(
            item["settingInstance"]["simpleSettingValue"]["value"]
        )

        try:
            with open(
                f"{self.script_data_path}{script_name}",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(decoded)
        except Exception as e:
            self.log(
                tag="error", msg=f"Error writing script {script_name} to file: {e}"
            )

    def main(self) -> dict[str, any]:
        """The main method to backup the Reusable Policy Settings

        Returns:
            dict[str, any]: The results of the backup
        """
        try:
            self.graph_data = self.make_graph_request(
                endpoint=self.endpoint + self.CONFIG_ENDPOINT,
                params={
                    "$select": "id,settinginstance,displayname,description,settingDefinitionId,version"
                },
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Reusable Policy Setting data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        for item in self.graph_data["value"]:
            if (
                item.get("settingDefinitionId")
                != "linux_customcompliance_discoveryscript_reusablesetting"
            ):
                continue

            if item.get("settingInstance").get("simpleSettingValue"):
                self._save_script(item)

        try:
            self.results = self.process_data(
                data=self.graph_data["value"],
                filetype=self.filetype,
                path=self.path,
                name_key="displayName",
                log_message=self.LOG_MESSAGE,
                audit_compare_info={"type": "resourceId", "value_key": "id"},
            )
        except Exception as e:
            self.log(
                tag="error", msg=f"Error processing Reusable Policy Setting data: {e}"
            )
            return None

        return self.results
