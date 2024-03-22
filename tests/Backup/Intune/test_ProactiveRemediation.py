# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.backup.Intune.ProactiveRemediation import (
    ProactiveRemediationScriptBackupModule,
)


class TestProactiveRemediationScriptBackupModule(unittest.TestCase):
    """Tests for the ProactiveRemediationScriptBackupModule class."""

    def setUp(self):
        self.module = ProactiveRemediationScriptBackupModule()

    @patch.object(ProactiveRemediationScriptBackupModule, "make_graph_request")
    @patch.object(ProactiveRemediationScriptBackupModule, "batch_request")
    @patch.object(ProactiveRemediationScriptBackupModule, "process_data")
    @patch.object(ProactiveRemediationScriptBackupModule, "_save_script")
    def test_main(
        self, _, mock_process_data, mock_batch_request, mock_make_graph_request
    ):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.return_value = {"value": [{"id": "object"}]}
        mock_batch_request.return_value = [{"id": "object", "publisher": "Myself"}]

        self.module.main()

        mock_make_graph_request.assert_called_once_with(
            endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT,
        )
        mock_process_data.assert_called_once_with(
            data=mock_batch_request.return_value,
            filetype=None,
            path=self.module.path,
            name_key="displayName",
            log_message="Backing up Proactive Remediation: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(ProactiveRemediationScriptBackupModule, "make_graph_request")
    @patch.object(ProactiveRemediationScriptBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            tag="error",
            msg=f"Error getting Proactive Remediation data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception",
        )

    @patch.object(ProactiveRemediationScriptBackupModule, "make_graph_request")
    @patch.object(ProactiveRemediationScriptBackupModule, "batch_request")
    @patch.object(ProactiveRemediationScriptBackupModule, "process_data")
    @patch.object(ProactiveRemediationScriptBackupModule, "_save_script")
    @patch.object(ProactiveRemediationScriptBackupModule, "log")
    def test_main_logs_exception_process_data(
        self,
        mock_log,
        _,
        mock_process_data,
        mock_batch_request,
        mock_make_graph_request,
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.return_value = {"value": [{"id": "object"}]}
        mock_batch_request.return_value = [{"id": "object", "publisher": "Myself"}]
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            tag="error",
            msg="Error processing Proactive Remediation data: Test exception",
        )


if __name__ == "__main__":
    unittest.main()
