# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.backup.Intune.Applications import ApplicationsBackupModule


class TestApplicationsBackupModule(unittest.TestCase):
    """Tests for the ApplicationsBackupModule class."""

    def setUp(self):
        self.module = ApplicationsBackupModule()
        self.app_data = {
            "id": "object",
            "@odata.type": "#microsoft.graph.iosStoreApp",
            "displayName": "Test App",
        }

    @patch.object(ApplicationsBackupModule, "make_graph_request")
    @patch.object(ApplicationsBackupModule, "process_data")
    @patch.object(ApplicationsBackupModule, "batch_assignment")
    @patch.object(ApplicationsBackupModule, "make_audit_request")
    def test_main(
        self,
        mock_make_audit_request,
        mock_batch_assignment,
        mock_process_data,
        mock_make_graph_request,
    ):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.side_effect = [
            {"value": [self.app_data]},
            {"responses": []},
        ]
        mock_batch_assignment.return_value = []
        mock_make_audit_request.return_value = []

        self.module.main()

        self.assertEqual(mock_make_graph_request.call_count, 2)
        mock_process_data.assert_called_once_with(
            data=self.app_data,
            filetype=None,
            path="None/Applications/iOS/",
            name_key="displayName",
            log_message="Backing up Application: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(ApplicationsBackupModule, "make_graph_request")
    @patch.object(ApplicationsBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            tag="error",
            msg=f"Error getting Application data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception",
        )

    @patch.object(ApplicationsBackupModule, "make_graph_request")
    @patch.object(ApplicationsBackupModule, "process_data")
    @patch.object(ApplicationsBackupModule, "batch_assignment")
    @patch.object(ApplicationsBackupModule, "make_audit_request")
    @patch.object(ApplicationsBackupModule, "log")
    def test_main_logs_exception_process_data(
        self,
        mock_log,
        mock_make_audit_request,
        mock_batch_assignment,
        mock_process_data,
        mock_make_graph_request,
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.side_effect = [
            {"value": [self.app_data]},
            {"responses": []},
        ]
        mock_process_data.side_effect = Exception("Test exception")
        mock_batch_assignment.return_value = []
        mock_make_audit_request.return_value = []

        self.module.main()

        mock_log.assert_called_with(
            tag="error", msg="Error processing Application data: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
