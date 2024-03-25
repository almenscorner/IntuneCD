# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class ComplianceUpdateModule(BaseUpdateModule):
    """A class used to update Intune compliance

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/compliancePolicies/"

    def __init__(self, *args, **kwargs):
        """Initializes the ComplianceUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Compliance Policies/Policies/"
        self.assignment_endpoint = "/deviceManagement/compliancePolicies/"
        self.assignment_extra_url = "/assign"
        self.exclude_paths = [
            "root['scheduledActionsForRule']",
            "root['settings']",
            "root['settings@odata.context']",
            "root['detectionScriptName']",
            "root['scheduledActionConfigurations']",
            "root['scheduledActionConfigurations'][0]['id']",
            "root['assignments']",
            "root['scheduledActionsForRule'][0]['scheduledActionConfigurations']",
        ]

    def _remove_compliance_keys(self, data: dict) -> dict[str, any]:
        """Removes additional keys from the compliance data

        Args:
            data (dict): The data to remove the keys from

        Returns:
            dict[str, any]: The data with the keys removed
        """
        if isinstance(data, dict):
            return {
                k: self._remove_compliance_keys(v)
                for k, v in data.items()
                if k
                not in [
                    "settingValueTemplateReference",
                    "settingInstanceTemplateReference",
                    "note",
                    "settingCount",
                    "creationSource",
                    "settings@odata.context",
                    "detectionScriptName",
                ]
            }
        if isinstance(data, list):
            return [self._remove_compliance_keys(v) for v in data]

        return data

    def _get_detection_script_id_path(self, data: dict, path: list = None) -> list:
        """Gets the path of the detection script id

        Args:
            data (dict): The data to get the path from
            path (list, optional): The path to the detection script id. Defaults to None.

        Returns:
            list: The path of the detection script id
        """
        if path is None:
            path = []
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict):
                    new_path = self._get_detection_script_id_path(v, path + [k])
                    if new_path is not None:
                        return new_path
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        new_path = self._get_detection_script_id_path(
                            item, path + [k, i]
                        )
                        if new_path is not None:
                            return new_path
                elif v == "linux_customcompliance_discoveryscript":
                    return path
        return None

    def _set_value_from_path(
        self, repo_data: dict, value: str, path: list
    ) -> dict[str, any]:
        """Sets the value from the path

        Args:
            repo_data (dict): The data to set the value in
            value (str): The value to set
            path (list): The path to set the value in

        Returns:
            dict[str, any]: The data with the value set
        """
        item = repo_data
        for key in path[:-1]:
            if isinstance(item, list):
                item = item[int(key)]
            else:
                item = item[key]
        if isinstance(item, list):
            item[int(path[-1])] = value
        else:
            item[path[-1]] = value
        return repo_data

    def _set_detection_script_id(self, repo_data: dict) -> dict[str, any]:
        """Sets the detection script id

        Args:
            repo_data (dict): The data to set the detection script id in

        Returns:
            dict[str, any]: The data with the detection script id set
        """
        # get detection script id
        script_id = self.make_graph_request(
            self.endpoint + "/beta/deviceManagement/reusablePolicySettings/",
            {"$filter": f"displayName eq '{repo_data['detectionScriptName']}'"},
        )
        if script_id.get("value"):
            script_id_path = self._get_detection_script_id_path(repo_data)
            script_id_path = script_id_path + ["simpleSettingValue", "value"]
            repo_data = self._set_value_from_path(
                repo_data, script_id["value"][0]["id"], script_id_path
            )

            return repo_data

        return False

    def _get_scheduledActionsForRule(self, intune_data: dict) -> dict[str, any]:
        """Gets the scheduled actions for the rule

        Args:
            intune_data (dict): The Intune data to get the scheduled actions for

        Returns:
            dict[str, any]: The Intune data with the scheduled actions for the rule
        """
        new_intune_data = []
        for item in intune_data["value"]:
            actions = self.make_graph_request(
                endpoint=self.endpoint
                + self.CONFIG_ENDPOINT
                + item["id"]
                + "/scheduledActionsForRule",
                params={"$expand": "scheduledActionConfigurations"},
            )
            for action in actions["value"]:
                self.remove_keys(action)

            item["scheduledActionsForRule"] = actions["value"]
            new_intune_data.append(item)

        return new_intune_data

    def _detection_script_check(self, repo_data: dict) -> None:
        """Checks if the detection script exists

        Args:
            repo_data (dict): The data to check the detection script for
        """
        if "detectionScriptName" in repo_data:
            script_name = repo_data["detectionScriptName"]
            repo_data = self._set_detection_script_id(repo_data)
            if repo_data is False:
                self.log(
                    tag="warning",
                    msg=f"Detection script {script_name} not found, Compliance Policy {self.name} not updated",
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
                self.update_downstream_data(
                    config_endpoint=self.endpoint
                    + self.CONFIG_ENDPOINT
                    + self.downstream_id
                    + "/setScheduledActions",
                    method="post",
                    data={"scheduledActions": repo_data["scheduledActionsForRule"]},
                    status_code=200,
                )

                self.update_diff_data(action_diff)

    def _settings_diff_check(self, repo_data: dict) -> None:
        """Checks the settings for differences

        Args:
            repo_data (dict): The data to check the settings for
        """
        if repo_data.get("settings"):
            for intune_setting, repo_setting in zip(
                self.downstream_object.get("settings"),
                repo_data["settings"],
            ):
                setting_diff = self.get_diffs(repo_setting, intune_setting, None)

                if setting_diff:
                    self.update_downstream_data(
                        config_endpoint=self.endpoint
                        + self.CONFIG_ENDPOINT
                        + self.downstream_id,
                        method="put",
                        data=repo_data,
                        status_code=204,
                    )

                    self.update_diff_data(setting_diff)

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
            self.params = {"$expand": "settings"}
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
                # reset params
                self.params = None
                self.create_request = None
                self.notify = True
                self.config_type = "Compliance Policy"

                repo_data = self.load_repo_data(filename)
                if repo_data:
                    self.create_request = None
                    if "technologies" not in repo_data:
                        continue
                    self.match_info = {
                        "name": repo_data.get("name"),
                        "technologies": repo_data.get("technologies"),
                    }
                    self.name = repo_data.get("name")
                    diff_data = self.create_diff_data(self.name, self.config_type)

                    # Check if detection script exists
                    repo_data = self._detection_script_check(repo_data)
                    if repo_data is False:
                        continue
                    # Get the scheduled actions for the rule
                    intune_data["value"] = self._get_scheduledActionsForRule(
                        intune_data
                    )

                    for rule in repo_data.get("scheduledActionsForRule"):
                        self._get_notification_template_id(rule)

                    # Remove additional keys from the data
                    new_intune_data = []
                    for item in intune_data["value"]:
                        item = self._remove_compliance_keys(item)
                        new_intune_data.append(item)
                    intune_data["value"] = new_intune_data
                    repo_data = self._remove_compliance_keys(repo_data)

                    for item in intune_data["value"]:
                        for action in item["scheduledActionsForRule"][0][
                            "scheduledActionConfigurations"
                        ]:
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
                    # If a match is found, check for differences on the scheduled actions and settings
                    if self.downstream_object:
                        self.notify = False
                        self.config_type = "Compliance Policy Scheduled Actions"
                        self._scheduledActionsForRule_diff_check(repo_data)
                        self.config_type = "Compliance Policy Settings"
                        repo_data.pop("assignments", None)
                        self._settings_diff_check(repo_data)
                    # If a new compliance policy is created, set the scheduled actions
                    if self.create_request:
                        self.update_downstream_data(
                            config_endpoint=self.endpoint
                            + self.CONFIG_ENDPOINT
                            + self.create_request["id"]
                            + "/setScheduledActions",
                            method="post",
                            data={
                                "scheduledActions": repo_data["scheduledActionsForRule"]
                            },
                            status_code=200,
                        )

                    self.set_diff_data(diff_data)
                    self.diff_summary.append(diff_data)
                    self.reset_diffs_and_count()

            self.remove_downstream_data(self.CONFIG_ENDPOINT, intune_data["value"])

        return self.diff_summary
