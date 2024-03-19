# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.backup.Intune.PowershellScripts import PowershellScriptsBackupModule


class TestPowershellScriptsBackupModule(unittest.TestCase):
    """Tests for the PowershellScriptsBackupModule class."""

    def setUp(self):
        self.module = PowershellScriptsBackupModule()

    @patch.object(PowershellScriptsBackupModule, "make_graph_request")
    @patch.object(PowershellScriptsBackupModule, "batch_request")
    @patch.object(PowershellScriptsBackupModule, "process_data")
    @patch.object(PowershellScriptsBackupModule, "_save_script")
    def test_main(
        self, _, mock_process_data, mock_batch_request, mock_make_graph_request
    ):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.return_value = {"value": [{"id": "object"}]}
        mock_batch_request.return_value = {"responses": [{"id": "object"}]}

        self.module.main()

        mock_make_graph_request.assert_called_once_with(
            endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT,
        )
        mock_process_data.assert_called_once_with(
            data=mock_batch_request.return_value,
            filetype=None,
            path=self.module.path,
            name_key="displayName",
            log_message="Backing up Powershell Script: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(PowershellScriptsBackupModule, "make_graph_request")
    @patch.object(PowershellScriptsBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg=f"Error getting Powershell Script data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception"
        )

    @patch.object(PowershellScriptsBackupModule, "process_data")
    @patch.object(PowershellScriptsBackupModule, "make_graph_request")
    @patch.object(PowershellScriptsBackupModule, "batch_request")
    @patch.object(PowershellScriptsBackupModule, "_save_script")
    @patch.object(PowershellScriptsBackupModule, "log")
    def test_main_logs_exception_process_data(
        self,
        mock_log,
        _,
        mock_batch_request,
        mock_make_graph_request,
        mock_process_data,
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.return_value = {"value": [{"id": "object"}]}
        mock_batch_request.return_value = {"responses": [{"id": "object"}]}
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg="Error processing Powershell Script data: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
