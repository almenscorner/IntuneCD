# -*- coding: utf-8 -*-
import glob
import json

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class ManagementIntentsUpdateModule(BaseUpdateModule):
    """A class used to update Intune Management Intents

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/"

    def __init__(self, *args, **kwargs):
        """Initializes the ManagementIntentsUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Management Intents/"
        self.config_type = "Management Intent"
        self.assignment_endpoint = "/deviceManagement/intents/"
        self.assignment_extra_url = "/assign"
        self.exclude_paths = [
            "root['assignments']",
        ]
        self.get_match = False
        self.assignment_status_code = 204
        self.diff_data = {
            "type": "",
            "name": "",
            "diffs": [],
            "count": 0,
        }

    def _build_request_data(
        self, repo_setting: dict[str, any], intune_setting_id: str
    ) -> dict[str, any]:
        # Create dict that we will use as the request json
        if "value" not in repo_setting:
            intent_type = "valueJson"
            value = repo_setting["valueJson"]
        else:
            intent_type = "value"
            value = repo_setting["value"]
        settings = {
            "settings": [
                {
                    "id": intune_setting_id,
                    "definitionId": repo_setting["definitionId"],
                    "@odata.type": repo_setting["@odata.type"],
                    intent_type: value,
                }
            ]
        }

        return settings

    def _handle_diffs(
        self,
        repo_setting: dict[str, any],
        intune_intent: dict[str, any],
        intune_setting_id: str,
    ) -> dict[str, any]:
        for intune_setting in intune_intent["settingsDelta"]:
            if repo_setting["definitionId"] == intune_setting["definitionId"]:
                diff = self.get_diffs(repo_setting, intune_setting)

        # If any changed values are found, push them to Intune
        if diff:
            # Create dict that we will use as the request json
            settings = self._build_request_data(repo_setting, intune_setting_id)
            request_data = json.dumps(settings)
            self.make_graph_request(
                self.endpoint
                + self.CONFIG_ENDPOINT
                + "intents/"
                + intune_intent["id"]
                + "/updateSettings",
                method="post",
                status_code=204,
                data=request_data,
            )

            self.diff_data["diffs"].extend(diff)
            self.diff_data["count"] += len(diff)

    def _create_intent(self, repo_data: dict[str, any]) -> dict[str, any]:
        template_id = repo_data["templateId"]
        repo_data.pop("templateId")
        request_json = json.dumps(repo_data)
        create_request = self.make_graph_request(
            endpoint=self.endpoint
            + self.CONFIG_ENDPOINT
            + "templates/"
            + template_id
            + "/createInstance",
            data=request_json,
            method="post",
        )

        if repo_data.get("assignments"):
            self.handle_assignments(
                repo_data["assignments"], [], "assignments", create_request["id"]
            )

    def main(self) -> dict[str, any]:
        """The main method to update the Intune data"""
        if self.path_exists():
            try:
                intune_data = self.get_downstream_data(self.CONFIG_ENDPOINT + "intents")
            except Exception as e:
                self.log(tag="error", msg=f"Error getting {self.config_type} data: {e}")
                return None

            intents = self.batch_intents(intune_data)

            self.downstream_assignments = self.batch_assignment(
                intents["value"],
                self.assignment_endpoint,
                "/assignments",
            )

            # Set glob pattern
            pattern = self.path + "*/*"
            for filename in glob.glob(pattern, recursive=True):
                self.notify = True
                repo_data = self.load_repo_data(filename)
                if repo_data:
                    if (
                        repo_data.get("templateId")
                        == "e44c2ca3-2f9a-400a-a113-6cc88efd773d"
                    ):
                        self.log(
                            msg="Endpoint detection and response is currently not supported...",
                        )
                        continue

                    self.match_info = {
                        "displayName": repo_data.get("displayName"),
                        "templateId": repo_data.get("templateId"),
                    }
                    self.name = repo_data.get("displayName")

                    self.diff_data["type"] = self.config_type
                    self.diff_data["name"] = self.name

                    intune_intent, intune_id = self.get_match_data(
                        intents["value"], self.match_info
                    )

                    if intune_intent:
                        self.log(
                            msg=f"Checking if Intent: {self.name} has any updates",
                        )

                        for repo_setting in repo_data["settingsDelta"]:
                            self.notify = False
                            self._handle_diffs(repo_setting, intune_intent, intune_id)

                        self.handle_assignments(
                            repo_data.get("assignments", {}),
                            self.downstream_assignments,
                            "assignments",
                            intune_id,
                        )

                    else:
                        self.log(
                            msg=f"Intent not found, creating new intent: {self.name}",
                        )
                        self._create_intent(repo_data)

                    self.diff_summary.append(self.diff_data)

            self.remove_downstream_data(
                f"{self.CONFIG_ENDPOINT}intents/", intents["value"]
            )

        return self.diff_summary
