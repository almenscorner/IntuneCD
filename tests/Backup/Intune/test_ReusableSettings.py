# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.backup.Intune.ReusableSettings import ReusableSettingsBackupModule


class TestReusableSettingsBackupModule(unittest.TestCase):
    """Tests for the ReusableSettingsBackupModule class."""

    def setUp(self):
        self.module = ReusableSettingsBackupModule()

    @patch.object(ReusableSettingsBackupModule, "make_graph_request")
    @patch.object(ReusableSettingsBackupModule, "process_data")
    @patch.object(ReusableSettingsBackupModule, "_save_script")
    def test_main(self, _, mock_process_data, mock_make_graph_request):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.return_value = {
            "value": [
                {
                    "displayName": "Test",
                    "settingDefinitionId": "linux_customcompliance_discoveryscript_reusablesetting",
                    "id": "object",
                    "settingInstance": {"simpleSettingValue": {"value": "value"}},
                }
            ]
        }

        self.module.main()

        mock_make_graph_request.assert_called_once_with(
            endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT,
            params={
                "$select": "id,settinginstance,displayname,description,settingDefinitionId,version"
            },
        )
        mock_process_data.assert_called_once_with(
            data=mock_make_graph_request.return_value["value"],
            filetype=None,
            path=self.module.path,
            name_key="displayName",
            log_message="Backing up Reusable Policy Setting: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(ReusableSettingsBackupModule, "make_graph_request")
    @patch.object(ReusableSettingsBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            tag="error",
            msg=f"Error getting Reusable Policy Setting data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception",
        )

    @patch.object(ReusableSettingsBackupModule, "make_graph_request")
    @patch.object(ReusableSettingsBackupModule, "process_data")
    @patch.object(ReusableSettingsBackupModule, "log")
    @patch.object(ReusableSettingsBackupModule, "_save_script")
    def test_main_logs_exception_process_data(
        self, _, mock_log, mock_process_data, mock_make_graph_request
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.return_value = {
            "value": [
                {
                    "displayName": "Test",
                    "settingDefinitionId": "linux_customcompliance_discoveryscript_reusablesetting",
                    "id": "object",
                    "settingInstance": {"simpleSettingValue": {"value": "value"}},
                }
            ]
        }
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            tag="error",
            msg="Error processing Reusable Policy Setting data: Test exception",
        )


if __name__ == "__main__":
    unittest.main()
