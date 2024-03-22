# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class DeviceComplianceBackupModule(BaseBackupModule):
    """A class used to backup Intune Device Compliance Policies

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/compliancePolicies"
    LOG_MESSAGE = "Backing up Compliance: "

    def __init__(self, *args, **kwargs):
        """Initializes the DeviceComplianceBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Compliance Policies/Policies/"
        self.audit_filter = (
            self.audit_filter or "componentName eq 'DeviceCompliancePolicy'"
        )
        self.assignment_endpoint = (
            self.assignment_endpoint or "deviceManagement/compliancePolicies/"
        )
        self.assignment_extra_url = self.assignment_extra_url or "/assignments"

    def _check_linux_discovery_script(self, data: dict) -> bool:
        """Checks if the data is a Linux discovery script

        Args:
            data (dict): The data to check

        Returns:
            bool: If the data is a Linux discovery script
        """
        if isinstance(data, dict):
            if "linux_customcompliance_discoveryscript" in data.values():
                return True
            return any(self._check_linux_discovery_script(v) for v in data.values())
        if isinstance(data, list):
            return any(self._check_linux_discovery_script(v) for v in data)
        return False

    def _get_detection_script_id(self, data: dict, path=None) -> list:
        """Gets the detection script ID path from the data

        Args:
            data (dict): The data to get the detection script ID from
            path (_type_, optional): The path to the detection script ID

        Returns:
            list: The path to the detection script ID
        """
        if path is None:
            path = []
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict):
                    new_path = self._get_detection_script_id(v, path + [k])
                    if new_path is not None:
                        return new_path
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        new_path = self._get_detection_script_id(item, path + [k, i])
                        if new_path is not None:
                            return new_path
                elif v == "linux_customcompliance_discoveryscript":
                    return path
        return None

    def _get_value_from_path(self, data: dict, path: list) -> str:
        """Gets the value from the path in the data

        Args:
            data (dict): The data to get the value from
            path (list): The path to the value

        Returns:
            str: The value from the path
        """
        for key in path:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data[key]
        return data["simpleSettingValue"]["value"]

    def _get_notification_template(self, rule: dict[str, any]) -> dict[str, any]:
        """Gets the notification template for a rule

        Args:
            rule (dict[str, any]): The rule to get the notification template for

        Returns:
            dict[str, any]: The notification template
        """
        for action in rule["scheduledActionConfigurations"]:
            if (
                action.get("notificationTemplateId")
                != "00000000-0000-0000-0000-000000000000"
            ):
                notification_template = self.make_graph_request(
                    self.endpoint
                    + "/beta/deviceManagement/notificationMessageTemplates/"
                    + action["notificationTemplateId"]
                )
                if notification_template:
                    action["notificationTemplateName"] = notification_template[
                        "displayName"
                    ]

    def main(self) -> dict[str, any]:
        """The main method to backup the Device Compliance Policies

        Returns:
            dict[str, any]: The results of the backup
        """
        try:
            self.graph_data = self.make_graph_request(
                endpoint=self.endpoint + self.CONFIG_ENDPOINT,
                params={
                    "$expand": "settings",
                },
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Compliance Policy data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        for item in self.graph_data["value"]:
            # Is the policy a Linux discovery script?
            if self._check_linux_discovery_script(item):
                # Get the detection script ID
                detection_script_id_path = self._get_detection_script_id(item)
                if detection_script_id_path is not None:
                    detection_script_id = self._get_value_from_path(
                        item, detection_script_id_path
                    )
                    # get the script name
                    detection_script = self.make_graph_request(
                        endpoint=self.endpoint
                        + "/beta/deviceManagement/reusablePolicySettings/",
                        params={"$filter": f"id eq '{detection_script_id}'"},
                    )
                    if detection_script["value"]:
                        item["detectionScriptName"] = detection_script["value"][0][
                            "displayName"
                        ]
                    else:
                        item["detectionScriptName"] = None

            # get scheduledActionsForRule
            scheduledActionsForRule = self.make_graph_request(
                endpoint=f"{self.endpoint + self.CONFIG_ENDPOINT}/{item['id']}/scheduledActionsForRule",
                params={"$expand": "scheduledActionConfigurations"},
            )
            item["scheduledActionsForRule"] = scheduledActionsForRule["value"]

            for action in item["scheduledActionsForRule"]:
                self.remove_keys(action)
                self._get_notification_template(action)
            for config in item["scheduledActionsForRule"][0][
                "scheduledActionConfigurations"
            ]:
                self.remove_keys(config)

        try:
            self.results = self.process_data(
                data=self.graph_data["value"],
                filetype=self.filetype,
                path=self.path,
                name_key="name",
                log_message=self.LOG_MESSAGE,
                audit_compare_info={"type": "resourceId", "value_key": "id"},
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing Compliance Policy data: {e}")
            return None

        return self.results
