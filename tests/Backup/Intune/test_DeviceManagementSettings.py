# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.backup.Intune.DeviceManagementSettings import (
    DeviceManagementSettingsBackupModule,
)


class TestDeviceManagementSettingsBackupModule(unittest.TestCase):
    """Tests for the DeviceManagementSettingsBackupModule class."""

    def setUp(self):
        self.module = DeviceManagementSettingsBackupModule()

    @patch.object(DeviceManagementSettingsBackupModule, "make_graph_request")
    @patch.object(DeviceManagementSettingsBackupModule, "process_data")
    def test_main(self, mock_process_data, mock_make_graph_request):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.return_value = {"value": [{"id": "object"}]}

        self.module.main()

        mock_make_graph_request.assert_called_once_with(
            endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT,
        )
        mock_process_data.assert_called_once_with(
            data=mock_make_graph_request.return_value,
            filetype=None,
            path="None/Device Management Settings/",
            name_key="",
            log_message=None,
            audit_compare_info={
                "type": "auditResourceType",
                "value_key": "Microsoft.Management.Services.Api.ApplePushNotificationCertificate",
            },
        )

    @patch.object(DeviceManagementSettingsBackupModule, "make_graph_request")
    @patch.object(DeviceManagementSettingsBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg=f"Error getting Device Management Settings data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception"
        )

    @patch.object(DeviceManagementSettingsBackupModule, "process_data")
    @patch.object(DeviceManagementSettingsBackupModule, "make_graph_request")
    @patch.object(DeviceManagementSettingsBackupModule, "log")
    def test_main_logs_exception_process_data(
        self, mock_log, mock_make_graph_request, mock_process_data
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.return_value = {"value": [{"id": "object"}]}
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg="Error processing Device Management Settings data: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
