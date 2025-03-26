# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class DeviceComplianceUpdateModule(BaseUpdateModule):
    """A class used to update Intune Device Compliance

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceCompliancePolicies/"

    def __init__(self, *args, **kwargs):
        """Initializes the DeviceComplianceUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Compliance Policies/Policies/"
        self.assignment_endpoint = "/deviceManagement/deviceCompliancePolicies/"
        self.assignment_extra_url = "/assign"
        self.exclude_paths = [
            "root['assignments']",
            "root['scheduledActionsForRule']",
            "root['deviceComplianceScriptName']",
            "root['scheduledActionConfigurations']",
            "root['scheduledActionConfigurations'][0]['id']",
            "root['assignments']",
            "root['scheduledActionsForRule'][0]['scheduledActionConfigurations']",
        ]
        self.params = {
            "expand": "scheduledActionsForRule($expand=scheduledActionConfigurations)"
        }

    def _set_compliance_script_id(self, data: dict) -> dict[str, any]:
        compliance_script_id = self.make_graph_request(
            endpoint=self.endpoint + "/beta/deviceManagement/deviceComplianceScripts",
            params={
                "$filter": f"displayName eq '{data['deviceComplianceScriptName']}'"
            },
        )
        if compliance_script_id.get("value"):
            data["deviceCompliancePolicyScript"][
                "deviceComplianceScriptId"
            ] = compliance_script_id["value"][0]["id"]

            return data

        return False

    def _compliance_script_check(self, repo_data: dict) -> dict[str, any]:
        """Checks if the detection script exists

        Args:
            repo_data (dict): The data to check the detection script for
        """
        if "deviceComplianceScriptName" in repo_data:
            script_name = repo_data["deviceComplianceScriptName"]
            repo_data = self._set_compliance_script_id(repo_data)
            if repo_data is False:
                print(
                    f"Detection script {script_name} not found, Compliance Policy {self.name} not updated"
                )

        return repo_data

    def _scheduledActionsForRule_diff_check(self, repo_data: dict) -> None:
        """Checks the scheduled actions for the rule for differences

        Args:
            repo_data (dict): The data to check the scheduled actions for the rule for
        """
        for intune_action, repo_action in zip(
            self.downstream_object.get("scheduledActionsForRule"),
            repo_data["scheduledActionsForRule"],
        ):
            action_diff = self.get_diffs(repo_action, intune_action, None)

            if action_diff:
                data = {
                    "deviceComplianceScheduledActionForRules": [
                        {
                            "ruleName": "PasswordRequired",
                            "scheduledActionConfigurations": repo_data[
                                "scheduledActionsForRule"
                            ][0]["scheduledActionConfigurations"],
                        }
                    ]
                }
                self.update_downstream_data(
                    config_endpoint=self.endpoint
                    + self.CONFIG_ENDPOINT
                    + self.downstream_id
                    + "/scheduleActionsForRules",
                    method="post",
                    data=data,
                    status_code=200,
                )

                self.update_diff_data(action_diff)

    def _get_notification_template_id(self, rule: dict[str, any]) -> dict[str, any]:
        """Gets the notification template for a rule

        Args:
            rule (dict[str, any]): The rule to get the notification template for

        Returns:
            dict[str, any]: The notification template
        """
        for action in rule["scheduledActionConfigurations"]:
            if action.get("notificationTemplateName"):
                notification_template = self.make_graph_request(
                    self.endpoint
                    + "/beta/deviceManagement/notificationMessageTemplates/",
                    params={
                        "$filter": f"displayName eq '{action['notificationTemplateName']}'"
                    },
                )
                if notification_template["value"]:
                    action["notificationTemplateId"] = notification_template["value"][
                        0
                    ]["id"]
                else:
                    action[
                        "notificationTemplateId"
                    ] = "00000000-0000-0000-0000-000000000000"

                action.pop("notificationTemplateName")

        return rule

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

            for filename in os.listdir(self.path):
                self.config_type = "Compliance Policy"
                self.notify = True
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    if repo_data.get("platforms") == "linux":
                        continue
                    self.match_info = {
                        "displayName": repo_data.get("displayName"),
                        "@odata.type": repo_data.get("@odata.type"),
                    }
                    self.name = repo_data.get("displayName")
                    diff_data = self.create_diff_data(self.name, self.config_type)

                    repo_data = self._compliance_script_check(repo_data)
                    if repo_data is False:
                        continue

                    for rule in repo_data.get("scheduledActionsForRule"):
                        self._get_notification_template_id(rule)

                    for item in intune_data.get(
                        "value", []
                    ):  # Ensure "value" exists and is iterable
                        actions = item.get("scheduledActionsForRule", [])

                        if actions:  # Ensure actions is not None and not empty
                            first_action = actions[0].get(
                                "scheduledActionConfigurations", []
                            )

                            if (
                                first_action
                            ):  # Ensure scheduledActionConfigurations is not None
                                for action in first_action:
                                    self.remove_keys(action)

                    try:
                        self.process_update(
                            downstream_data=intune_data["value"],
                            repo_data=repo_data,
                            method="patch",
                            status_code=204,
                            config_endpoint=self.CONFIG_ENDPOINT,
                        )
                    except Exception as e:
                        self.log(
                            tag="error",
                            msg=f"Error updating {self.config_type} {self.name}: {e}",
                        )

                    if self.downstream_object:
                        self.notify = False
                        self.config_type = "Compliance Policy Scheduled Actions"
                        self._scheduledActionsForRule_diff_check(repo_data)

                    self.set_diff_data(diff_data)
                    self.diff_summary.append(diff_data)
                    self.reset_diffs_and_count()

            self.remove_downstream_data(self.CONFIG_ENDPOINT, intune_data["value"])

        return self.diff_summary
