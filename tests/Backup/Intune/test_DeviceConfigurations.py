# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.backup.Intune.DeviceConfigurations import (
    DeviceConfigurationBackupModule,
)


class TestDeviceConfigurationBackupModule(unittest.TestCase):
    """Tests for the DeviceConfigurationBackupModule class."""

    def setUp(self):
        self.module = DeviceConfigurationBackupModule()

    @patch.object(DeviceConfigurationBackupModule, "make_graph_request")
    @patch.object(DeviceConfigurationBackupModule, "process_data")
    def test_main(self, mock_process_data, mock_make_graph_request):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.return_value = {
            "value": [{"id": "object", "@odata.type": "test"}]
        }

        self.module.main()

        mock_make_graph_request.assert_called_once_with(
            endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT,
        )
        mock_process_data.assert_called_once_with(
            data=mock_make_graph_request.return_value["value"],
            filetype=None,
            path="None/Device Configurations/",
            name_key="displayName",
            log_message="Backing up Device Configuration: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(DeviceConfigurationBackupModule, "make_graph_request")
    @patch.object(DeviceConfigurationBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg=f"Error getting Device Configuration data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception"
        )

    @patch.object(DeviceConfigurationBackupModule, "process_data")
    @patch.object(DeviceConfigurationBackupModule, "make_graph_request")
    @patch.object(DeviceConfigurationBackupModule, "log")
    def test_main_logs_exception_process_data(
        self, mock_log, mock_make_graph_request, mock_process_data
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.return_value = {
            "value": [{"id": "object", "@odata.type": "test"}]
        }
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg="Error processing Device Configuration data: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
