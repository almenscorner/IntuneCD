# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.backup.Intune.RemoteAssistancePartner import (
    RemoteAssistancePartnerBackupModule,
)


class TestRemoteAssistancePartnerBackupModule(unittest.TestCase):
    """Tests for the RemoteAssistancePartnerBackupModule class."""

    def setUp(self):
        self.module = RemoteAssistancePartnerBackupModule()

    @patch.object(RemoteAssistancePartnerBackupModule, "make_graph_request")
    @patch.object(RemoteAssistancePartnerBackupModule, "process_data")
    def test_main(self, mock_process_data, mock_make_graph_request):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.return_value = {
            "value": [{"id": "object", "onboardingStatus": "Onboarded"}]
        }

        self.module.main()

        mock_make_graph_request.assert_called_once_with(
            endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT,
        )
        mock_process_data.assert_called_once_with(
            data=mock_make_graph_request.return_value["value"],
            filetype=None,
            path=self.module.path,
            name_key="displayName",
            log_message="Backing up Remote Assistance Partner: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(RemoteAssistancePartnerBackupModule, "make_graph_request")
    @patch.object(RemoteAssistancePartnerBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            tag="error",
            msg=f"Error getting Remote Assistance Partner data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception",
        )

    @patch.object(RemoteAssistancePartnerBackupModule, "process_data")
    @patch.object(RemoteAssistancePartnerBackupModule, "make_graph_request")
    @patch.object(RemoteAssistancePartnerBackupModule, "log")
    def test_main_logs_exception_process_data(
        self, mock_log, mock_make_graph_request, mock_process_data
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.return_value = {
            "value": [{"id": "object", "onboardingStatus": "Onboarded"}]
        }
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            tag="error",
            msg="Error processing Remote Assistance Partner data: Test exception",
        )


if __name__ == "__main__":
    unittest.main()
