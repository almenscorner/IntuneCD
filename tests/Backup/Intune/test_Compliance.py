# -*- coding: utf-8 -*-
import unittest
from unittest.mock import call, patch

from src.IntuneCD.backup.Intune.Compliance import ComplianceBackupModule


class TestComplianceBackupModule(unittest.TestCase):
    """Tests for the ComplianceBackupModule class."""

    def setUp(self):
        self.module = ComplianceBackupModule()
        self.module.exclude = []
        self.policy = {
            "value": [
                {
                    "id": "object",
                    "scheduledActionsForRule": [
                        {"id": "rule", "scheduledActionConfigurations": []}
                    ],
                    "deviceCompliancePolicyScript": {
                        "deviceComplianceScriptId": "1",
                    },
                }
            ]
        }

    @patch.object(ComplianceBackupModule, "make_graph_request")
    @patch.object(ComplianceBackupModule, "process_data")
    @patch.object(ComplianceBackupModule, "_get_notification_template")
    def test_main(self, _, mock_process_data, mock_make_graph_request):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.side_effect = [
            self.policy,
            {"displayName": "script"},
        ]

        self.module.main()

        mock_make_graph_request.assert_has_calls(
            [
                call(
                    endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT,
                    params={
                        "$expand": "scheduledActionsForRule($expand=scheduledActionConfigurations)"
                    },
                ),
                call(
                    self.module.endpoint
                    + "/beta/deviceManagement/deviceComplianceScripts/1"
                ),
            ]
        )
        mock_process_data.assert_called_once_with(
            data=self.policy["value"],
            filetype=None,
            path="None/Compliance Policies/Policies/",
            name_key="displayName",
            log_message="Backing up Compliance: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(ComplianceBackupModule, "make_graph_request")
    @patch.object(ComplianceBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            tag="error",
            msg=f"Error getting Compliance Policy data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception",
        )

    @patch.object(ComplianceBackupModule, "process_data")
    @patch.object(ComplianceBackupModule, "make_graph_request")
    @patch.object(ComplianceBackupModule, "log")
    def test_main_logs_exception_process_data(
        self, mock_log, mock_make_graph_request, mock_process_data
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.return_value = {
            "value": [{"id": "object", "scheduledActionsForRule": []}]
        }
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            tag="error", msg="Error processing Compliance Policy data: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
