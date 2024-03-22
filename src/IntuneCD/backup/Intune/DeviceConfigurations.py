# -*- coding: utf-8 -*-
import os

from ...intunecdlib.BaseBackupModule import BaseBackupModule


class DeviceConfigurationBackupModule(BaseBackupModule):
    """A class used to backup Intune Device Configurations

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
        LOG_MESSAGE (str): The message to log when backing up the data
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/deviceConfigurations"
    LOG_MESSAGE = "Backing up Device Configuration: "

    def __init__(self, *args, **kwargs):
        """Initializes the DeviceConfigurationBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Device Configurations/"
        self.audit_filter = "componentName eq 'DeviceConfiguration'"
        self.assignment_endpoint = "deviceManagement/deviceConfigurations/"
        self.assignment_extra_url = "/assignments"

    def main(self) -> dict[str, any]:
        """The main method to backup the Device Configurations

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
                msg=f"Error getting Device Configuration data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        custom_apple_odata = [
            "#microsoft.graph.macOSCustomConfiguration",
            "#microsoft.graph.iosCustomConfiguration",
        ]
        custom_windows_odata = ["#microsoft.graph.windows10CustomConfiguration"]

        for item in self.graph_data["value"]:
            if item["@odata.type"] in custom_apple_odata:
                decoded = self.decode_base64(item["payload"])
                try:
                    if not os.path.exists(self.path + "mobileconfig/"):
                        os.makedirs(self.path + "mobileconfig/")
                except Exception as e:
                    self.log(tag="error", msg=f"Error creating mobileconfig path: {e}")

                try:
                    f = open(
                        self.path + "mobileconfig/" + item["payloadFileName"],
                        "w",
                        encoding="utf-8",
                    )
                    f.write(decoded)
                except Exception as e:
                    self.log(
                        tag="error", msg=f"Error writing mobileconfig data to file: {e}"
                    )

            elif item["@odata.type"] in custom_windows_odata and item.get(
                "omaSettings"
            ):
                if not self.ignore_oma_settings:
                    omas = []
                    for setting in item["omaSettings"]:
                        if setting.get("isEncrypted"):
                            decoded_oma = {}
                            decoded_oma["@odata.type"] = setting["@odata.type"]
                            decoded_oma["displayName"] = setting["displayName"]
                            decoded_oma["description"] = setting["description"]
                            decoded_oma["omaUri"] = setting["omaUri"]
                            decoded_oma["isEncrypted"] = False
                            decoded_oma["secretReferenceValueId"] = None
                            oma_value = self.make_graph_request(
                                endpoint=self.endpoint
                                + self.CONFIG_ENDPOINT
                                + "/"
                                + item["id"]
                                + "/getOmaSettingPlainTextValue(secretReferenceValueId='"
                                + setting["secretReferenceValueId"]
                                + "')"
                            )
                            decoded_oma["value"] = oma_value
                            omas.append(decoded_oma)
                        else:
                            omas.append(setting)
                else:
                    omas = item["omaSettings"]

                item["omaSettings"] = omas

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
                tag="error", msg=f"Error processing Device Configuration data: {e}"
            )
            return None

        return self.results
