# -*- coding: utf-8 -*-
import unittest
from unittest.mock import call, patch

from src.IntuneCD.backup.Intune.GroupPolicyConfigurations import (
    GroupPolicyConfigurationsBackupModule,
)


class TestGroupPolicyConfigurationsBackupModule(unittest.TestCase):
    """Tests for the GroupPolicyConfigurationsBackupModule class."""

    def setUp(self):
        self.module = GroupPolicyConfigurationsBackupModule()
        self.expected_data = [
            {
                "id": "object",
                "definitionValues": [
                    {"id": "definition", "presentationValues": [{"id": "presentation"}]}
                ],
            }
        ]

    @patch.object(GroupPolicyConfigurationsBackupModule, "make_graph_request")
    @patch.object(GroupPolicyConfigurationsBackupModule, "process_data")
    def test_main(self, mock_process_data, mock_make_graph_request):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.side_effect = [
            {"value": [{"id": "object"}]},
            {"value": [{"id": "definition"}]},
            {"value": [{"id": "presentation"}]},
        ]

        self.module.main()

        mock_make_graph_request.assert_has_calls(
            [
                call(endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT),
                call(
                    endpoint=f"{self.module.endpoint}{self.module.CONFIG_ENDPOINT}/object/definitionValues?$expand=definition"
                ),
                call(
                    endpoint=f"{self.module.endpoint}{self.module.CONFIG_ENDPOINT}/object/definitionValues/definition/presentationValues?$expand=presentation"
                ),
            ]
        )
        mock_process_data.assert_called_once_with(
            data=self.expected_data,
            filetype=None,
            path=self.module.path,
            name_key="displayName",
            log_message="Backing up Device Configuration: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(GroupPolicyConfigurationsBackupModule, "make_graph_request")
    @patch.object(GroupPolicyConfigurationsBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg=f"Error getting Group Policy Configuration data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception"
        )

    @patch.object(GroupPolicyConfigurationsBackupModule, "process_data")
    @patch.object(GroupPolicyConfigurationsBackupModule, "make_graph_request")
    @patch.object(GroupPolicyConfigurationsBackupModule, "log")
    def test_main_logs_exception_process_data(
        self, mock_log, mock_make_graph_request, mock_process_data
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.side_effect = [
            {"value": [{"id": "object"}]},
            {"value": [{"id": "definition"}]},
            {"value": [{"id": "presentation"}]},
        ]
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg="Error processing Group Policy Configuration data: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
