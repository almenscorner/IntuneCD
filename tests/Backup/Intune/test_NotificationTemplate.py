# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.backup.Intune.NotificationTemplates import (
    NotificationTemplateBackupModule,
)


class TestNotificationTemplateBackupModule(unittest.TestCase):
    """Tests for the NotificationTemplateBackupModule class."""

    def setUp(self):
        self.module = NotificationTemplateBackupModule()

    @patch.object(NotificationTemplateBackupModule, "make_graph_request")
    @patch.object(NotificationTemplateBackupModule, "process_data")
    def test_main(self, mock_process_data, mock_make_graph_request):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.return_value = {
            "value": [
                {
                    "id": "object",
                    "localizedNotificationMessages": [{"id": "locale"}],
                }
            ]
        }

        self.module.main()

        mock_make_graph_request.assert_called_once_with(
            endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT,
            params="?$expand=localizedNotificationMessages",
        )
        mock_process_data.assert_called_once_with(
            data=mock_make_graph_request.return_value["value"],
            filetype=None,
            path="None/Compliance Policies/Message Templates/",
            name_key="displayName",
            log_message="Backing up Notification Message Template: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(NotificationTemplateBackupModule, "make_graph_request")
    @patch.object(NotificationTemplateBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg=f"Error getting Notification Template data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception"
        )

    @patch.object(NotificationTemplateBackupModule, "process_data")
    @patch.object(NotificationTemplateBackupModule, "make_graph_request")
    @patch.object(NotificationTemplateBackupModule, "log")
    def test_main_logs_exception_process_data(
        self, mock_log, mock_make_graph_request, mock_process_data
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.return_value = {
            "value": [
                {
                    "id": "object",
                    "localizedNotificationMessages": [{"id": "locale"}],
                }
            ]
        }
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg="Error processing Notification Template data: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
