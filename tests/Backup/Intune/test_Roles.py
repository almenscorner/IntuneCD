# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, call

from src.IntuneCD.backup.Intune.Roles import RolesBackupModule


class TestRolesBackupModule(unittest.TestCase):
    """Tests for the RolesBackupModule class."""

    def setUp(self):
        self.module = RolesBackupModule()
        self.module.exclude = []

    @patch.object(RolesBackupModule, "make_graph_request")
    @patch.object(RolesBackupModule, "_get_group_names")
    @patch.object(RolesBackupModule, "process_data")
    def test_main(
        self, mock_process_data, mock_get_group_names, mock_make_graph_request
    ):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.side_effect = [
            {"value": [{"id": "object", "rolePermissions": [{"actions": ["action"]}]}]},
            {
                "value": [
                    {"id": "1"},
                ]
            },
            {"scopeMembers": ["member"], "members": ["member"]},
        ]
        mock_get_group_names.side_effect = ["group name1", "group name2"]

        self.module.main()

        mock_make_graph_request.assert_has_calls(
            [
                call(
                    endpoint="https://graph.microsoft.com/beta/deviceManagement/roleDefinitions",
                    params={"$filter": "isBuiltIn eq false"},
                ),
                call(
                    "https://graph.microsoft.com/beta/deviceManagement/roleDefinitions/object/roleAssignments"
                ),
                call(
                    "https://graph.microsoft.com/beta/deviceManagement/roleAssignments/1"
                ),
            ]
        )
        mock_process_data.assert_called_once_with(
            data=[
                {
                    "id": "object",
                    "rolePermissions": [{}],
                    "roleAssignments": [
                        {"scopeMembers": "group name1", "members": "group name2"}
                    ],
                }
            ],
            filetype=None,
            path=self.module.path,
            name_key="displayName",
            log_message="Backing up Role: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(RolesBackupModule, "make_graph_request")
    @patch.object(RolesBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg=f"Error getting Role data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception"
        )

    @patch.object(RolesBackupModule, "process_data")
    @patch.object(RolesBackupModule, "make_graph_request")
    @patch.object(RolesBackupModule, "log")
    def test_main_logs_exception_process_data(
        self, mock_log, mock_make_graph_request, mock_process_data
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.return_value = {
            "value": [{"id": "object", "rolePermissions": [{"actions": ["action"]}]}]
        }
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(msg="Error processing Role data: Test exception")


if __name__ == "__main__":
    unittest.main()
