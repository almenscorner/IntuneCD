# -*- coding: utf-8 -*-
import unittest
from unittest.mock import call, patch

from src.IntuneCD.backup.Intune.AppConfiguration import AppConfigurationBackupModule


class TestAppConfigurationBackupModule(unittest.TestCase):
    """Tests for the AppConfigurationBackupModule class."""

    def setUp(self):
        self.module = AppConfigurationBackupModule()

    @patch.object(AppConfigurationBackupModule, "make_graph_request")
    @patch.object(AppConfigurationBackupModule, "process_data")
    def test_main(self, mock_process_data, mock_make_graph_request):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.side_effect = [
            {"value": [{"id": "object", "targetedMobileApps": {"id": "app1"}}]},
            {"id": "app1", "displayName": "app1", "@odata.type": "magic.app"},
        ]

        self.module.main()

        mock_make_graph_request.assert_has_calls(
            [
                call(endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT),
                call(endpoint=self.module.endpoint + self.module.APP_ENDPOINT + "/id"),
            ]
        )

        mock_process_data.assert_called_once_with(
            data=[
                {
                    "id": "object",
                    "targetedMobileApps": {"appName": "app1", "type": "magic.app"},
                }
            ],
            filetype=None,
            path="None/App Configuration/",
            name_key="displayName",
            log_message="Backing up App Configuration: ",
            audit_compare_info={"type": "resourceId", "value_key": "id"},
        )

    @patch.object(AppConfigurationBackupModule, "make_graph_request")
    @patch.object(AppConfigurationBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg=f"Error getting App Configuration data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception"
        )

    @patch.object(AppConfigurationBackupModule, "process_data")
    @patch.object(AppConfigurationBackupModule, "make_graph_request")
    @patch.object(AppConfigurationBackupModule, "log")
    def test_main_logs_exception_process_data(
        self, mock_log, mock_make_graph_request, mock_process_data
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.side_effect = [
            {"value": [{"id": "object", "targetedMobileApps": {"id": "app1"}}]},
            {"id": "app1", "displayName": "app1", "@odata.type": "magic.app"},
        ]
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg="Error processing App Configuration data: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
