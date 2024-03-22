# -*- coding: utf-8 -*-
from ...intunecdlib.BaseBackupModule import BaseBackupModule


class AutopilotDevicesBackupModule(BaseBackupModule):
    """A class used to backup Intune Autopilot Devices

    Attributes:
        CONFIG_ENDPOINT (str): The endpoint to get the data from
    """

    CONFIG_ENDPOINT = "/beta/deviceManagement/windowsAutopilotDeviceIdentities"

    def __init__(self, *args, **kwargs):
        """Initializes the AutopilotDevicesBackupModule class

        Args:
            *args: The positional arguments to pass to the base class's __init__ method.
            **kwargs: The keyword arguments to pass to the base class's __init__ method.
        """
        super().__init__(*args, **kwargs)
        self.path = f"{self.path}/Autopilot Devices/"
        self.append_id = False
        self.audit = False
        self.prefix = None
        # Autopilot Devices has no assignments, so exclude assignments from the run
        self.has_assignments = False

    def main(self) -> None:
        """The main method to backup the Autopilot Devices"""
        try:
            self.graph_data = self.make_graph_request(
                endpoint=self.endpoint + self.CONFIG_ENDPOINT
            )
        except Exception as e:
            self.log(
                tag="error",
                msg=f"Error getting Autopilot Device data from {self.endpoint + self.CONFIG_ENDPOINT}: {e}",
            )
            return None

        self.log(msg="Backing up Autopilot Devices")

        try:
            self.process_data(
                data=self.graph_data["value"],
                filetype=self.filetype,
                path=self.path,
                name_key="id",
                log_message=None,
            )
        except Exception as e:
            self.log(tag="error", msg=f"Error processing Autopilot Device data: {e}")
            return None
