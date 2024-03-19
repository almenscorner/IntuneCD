# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.backup.Intune.ComplianceScripts import ComplianceScriptsBackupModule


class TestComplianceScriptsBackupModule(unittest.TestCase):
    """Tests for the ComplianceScriptsBackupModule class."""

    def setUp(self):
        self.module = ComplianceScriptsBackupModule()

    @patch.object(ComplianceScriptsBackupModule, "make_graph_request")
    @patch.object(ComplianceScriptsBackupModule, "batch_request")
    @patch.object(ComplianceScriptsBackupModule, "process_data")
    @patch.object(ComplianceScriptsBackupModule, "_save_script")
    def test_main(
        self, _, mock_process_data, mock_batch_request, mock_make_graph_request
    ):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.return_value = {"value": [{"id": "object"}]}
        mock_batch_request.return_value = [
            {"detectionScriptContent": "test", "displayName": "test"}
        ]

        self.module.main()

        mock_make_graph_request.assert_called_once_with(
            endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT,
        )
        mock_process_data.assert_called_once_with(
            data=[{"detectionScriptContent": "test", "displayName": "test"}],
            filetype=None,
            path="None/Compliance Policies/Scripts/",
            name_key="displayName",
            log_message="Backing up Compliance Script: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(ComplianceScriptsBackupModule, "make_graph_request")
    @patch.object(ComplianceScriptsBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg=f"Error getting Compliance Script data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception"
        )

    @patch.object(ComplianceScriptsBackupModule, "process_data")
    @patch.object(ComplianceScriptsBackupModule, "make_graph_request")
    @patch.object(ComplianceScriptsBackupModule, "batch_request")
    @patch.object(ComplianceScriptsBackupModule, "log")
    @patch.object(ComplianceScriptsBackupModule, "_save_script")
    def test_main_logs_exception_process_data(
        self,
        _,
        mock_log,
        mock_batch_request,
        mock_make_graph_request,
        mock_process_data,
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.return_value = {"value": [{"id": "object"}]}
        mock_batch_request.return_value = [
            {"detectionScriptContent": "test", "displayName": "test"}
        ]
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg="Error processing Compliance Script data: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
