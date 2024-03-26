# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class ComplianceBackupModule(BaseBackupModule):
    """A class used to backup Intune Compliance Policies

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceCompliancePolicies/"
    LOG_MESSAGE = "Backing up Compliance: "

    def __init__(self, *args, **kwargs):
        """Initializes the ComplianceBackupModule class

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
            self.assignment_endpoint or "deviceManagement/deviceCompliancePolicies/"
        )
        self.assignment_extra_url = self.assignment_extra_url or "/assignments"

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

        return rule

    def main(self) -> dict[str, any]:
        """The main method to backup the Compliance Policies

        Returns:
            dict[str, any]: The results of the backup
        """
        try:
            self.graph_data = self.make_graph_request(
                endpoint=self.endpoint + self.CONFIG_ENDPOINT,
                params={
                    "$expand": "scheduledActionsForRule($expand=scheduledActionConfigurations)"
                },
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Compliance Policy data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        for item in self.graph_data["value"]:
            # Remove the keys that are not needed from each scheduledActionsForRule
            for rule in item["scheduledActionsForRule"]:
                self.remove_keys(rule)
                self._get_notification_template(rule)
                for action in rule["scheduledActionConfigurations"]:
                    self.remove_keys(action)

            # If there is a deviceCompliancePolicyScript, get the name of the script
            if item.get("deviceCompliancePolicyScript", None):
                # Get the name of the script
                script_name = self.make_graph_request(
                    self.endpoint
                    + "/beta/deviceManagement/deviceComplianceScripts/"
                    + item["deviceCompliancePolicyScript"]["deviceComplianceScriptId"]
                )
                if script_name:
                    item["deviceComplianceScriptName"] = script_name["displayName"]
                else:
                    item["deviceComplianceScriptName"] = None

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
            self.log(tag="error", msg=f"Error processing Compliance Policy data: {e}")
            return None

        return self.results
