# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseUpdateModule import BaseUpdateModule


class DeviceConfigurationsUpdateModule(BaseUpdateModule):
    """A class used to update Intune Device Configurations

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        APP_ENDPOINT (str): The endpoint to get the app data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceConfigurations/"

    def __init__(self, *args, **kwargs):
        """Initializes the DeviceConfigurationsUpdateModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Device Configurations/"
        self.assignment_endpoint = "/deviceManagement/deviceConfigurations/"
        self.assignment_extra_url = "/assign"
        self.exclude_paths = [
            "root['assignments']",
            "root['payload']",
            "root['isEncrypted']",
            "root['omaSettings']",
        ]

    def _handle_custom_apple_device_configuration(
        self, intune_data: dict[str, any], repo_data: dict[str, any]
    ) -> None:
        payload_path = self.path + "/mobileconfig/" + repo_data["payloadFileName"]
        if self.path_exists(payload_path):
            repo_payload_data = self.load_plist(payload_path)
            intune_decoded_payload_data = self.decode_base64(intune_data["payload"])
            self.write_temp_file(intune_decoded_payload_data)
            intune_payload_data = self.load_plist(self.path + "temp.mobileconfig")

            payload_diff = self.get_diffs(repo_payload_data, intune_payload_data, None)
            if payload_diff:
                self.update_downstream_data(
                    self.endpoint + self.CONFIG_ENDPOINT + self.downstream_id,
                    "patch",
                    204,
                    repo_data,
                )

                self.update_diff_data(payload_diff)

            self.remove_temp_file(self.path + "temp.mobileconfig")

    def _handle_custom_windows_device_configuration(
        self, intune_data: dict[str, any], repo_data: dict[str, any]
    ) -> None:
        omas = []
        oma_diff = None
        for setting in intune_data.get("omaSettings"):
            if setting["isEncrypted"]:
                decoded_oma = {}
                oma_value = self.make_graph_request(
                    endpoint=self.endpoint
                    + self.CONFIG_ENDPOINT
                    + "/"
                    + self.downstream_id
                    + "/getOmaSettingPlainTextValue(secretReferenceValueId='"
                    + setting["secretReferenceValueId"]
                    + "')",
                )
                decoded_oma["@odata.type"] = setting["@odata.type"]
                decoded_oma["displayName"] = setting["displayName"]
                decoded_oma["description"] = setting["description"]
                decoded_oma["omaUri"] = setting["omaUri"]
                decoded_oma["value"] = oma_value["value"]
                decoded_oma["isEncrypted"] = True
                decoded_oma["secretReferenceValueId"] = None
                omas.append(decoded_oma)
            elif not setting["isEncrypted"]:
                omas.append(setting)

        intune_data.pop("omaSettings")
        intune_data["omaSettings"] = omas

        for intune_omaSetting, repo_omaSetting in zip(
            intune_data.get("omaSettings"),
            repo_data["omaSettings"],
        ):
            oma_diff = self.get_diffs(
                repo_omaSetting, intune_omaSetting, ["root['isEncrypted']"]
            )

        if oma_diff:
            self.update_downstream_data(
                self.endpoint + self.CONFIG_ENDPOINT + self.downstream_id,
                "patch",
                204,
                repo_data,
            )

            self.update_diff_data(oma_diff)

    def _prepare_repo_omas(self, repo_data: dict[str, any]) -> dict[str, any]:
        repo_omas = []
        for repo_omaSetting in repo_data["omaSettings"]:
            if isinstance(repo_omaSetting["value"], dict):
                repo_omaSetting = self.remove_keys(repo_omaSetting)
                repo_omaSetting["value"] = repo_omaSetting["value"]["value"]
                repo_omas.append(repo_omaSetting)
            else:
                repo_omaSetting = self.remove_keys(repo_omaSetting)
                repo_omas.append(repo_omaSetting)
        repo_data.pop("omaSettings")
        repo_data["omaSettings"] = repo_omas

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

            custom_apple_odata_types = [
                "#microsoft.graph.iosCustomConfiguration",
                "#microsoft.graph.macOSCustomConfiguration",
            ]

            for filename in os.listdir(self.path):
                self.notify = True
                self.config_type = "Device Configuration"

                repo_data = self.load_repo_data(filename)
                if repo_data:
                    if "@odata.type" not in repo_data:
                        continue
                    self.match_info = {
                        "displayName": repo_data.get("displayName"),
                        "@odata.type": repo_data.get("@odata.type"),
                    }
                    self.name = repo_data.get("displayName")
                    diff_data = self.create_diff_data(self.name, self.config_type)

                    if (
                        repo_data["@odata.type"]
                        == "#microsoft.graph.windows10CustomConfiguration"
                    ):
                        self._prepare_repo_omas(repo_data)

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
                        if repo_data["@odata.type"] in custom_apple_odata_types:
                            self.notify = False
                            self.config_type = "Mobileconfig"
                            self._handle_custom_apple_device_configuration(
                                self.downstream_object, repo_data
                            )
                        if (
                            repo_data["@odata.type"]
                            == "#microsoft.graph.windows10CustomConfiguration"
                        ):
                            self.notify = False
                            self.config_type = "OMA-URI"
                            self._handle_custom_windows_device_configuration(
                                self.downstream_object, repo_data
                            )

                    self.set_diff_data(diff_data)
                    self.diff_summary.append(diff_data)
                    self.reset_diffs_and_count()

            self.remove_downstream_data(self.CONFIG_ENDPOINT, intune_data["value"])

        return self.diff_summary
