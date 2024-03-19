# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.backup.Intune.CustomAttributes import CustomAttributesBackupModule


class TestCustomAttributesBackupModule(unittest.TestCase):
    """Tests for the CustomAttributesBackupModule class."""

    def setUp(self):
        self.module = CustomAttributesBackupModule()

    @patch.object(CustomAttributesBackupModule, "_save_script")
    @patch.object(CustomAttributesBackupModule, "make_graph_request")
    @patch.object(CustomAttributesBackupModule, "batch_request")
    @patch.object(CustomAttributesBackupModule, "process_data")
    def test_main(
        self, mock_process_data, mock_batch_request, mock_make_graph_request, _
    ):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.return_value = {"value": [{"id": "object"}]}
        mock_batch_request.return_value = [
            {"scriptContent": "test", "displayName": "test", "fileName": "test.sh"}
        ]

        self.module.main()

        mock_make_graph_request.assert_called_once_with(
            endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT,
        )
        mock_process_data.assert_called_once_with(
            data=[
                {"scriptContent": "test", "displayName": "test", "fileName": "test.sh"}
            ],
            filetype=None,
            path="None/Custom Attributes/",
            name_key="displayName",
            log_message="Backing up Custom Attribute: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(CustomAttributesBackupModule, "make_graph_request")
    @patch.object(CustomAttributesBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg=f"Error getting Custom Attribute data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception"
        )

    @patch.object(CustomAttributesBackupModule, "_save_script")
    @patch.object(CustomAttributesBackupModule, "process_data")
    @patch.object(CustomAttributesBackupModule, "batch_request")
    @patch.object(CustomAttributesBackupModule, "make_graph_request")
    @patch.object(CustomAttributesBackupModule, "log")
    def test_main_logs_exception_process_data(
        self,
        mock_log,
        mock_make_graph_request,
        mock_batch_request,
        mock_process_data,
        _,
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.return_value = {"value": [{"id": "object"}]}
        mock_batch_request.return_value = [
            {"scriptContent": "test", "displayName": "test", "fileName": "test.sh"}
        ]
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg="Error processing Custom Attribute data: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
