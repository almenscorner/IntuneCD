# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.intunecdlib.BaseGraphModule import BaseGraphModule


class TestBaseGraphModuleAssignments(unittest.TestCase):
    """Tests for assignment comparison and normalization."""

    def setUp(self):
        self.module = BaseGraphModule()

    def test_get_object_assignment_preserves_group_id_for_update_comparison(self):
        responses = [
            {
                "@odata.context": (
                    "https://graph.microsoft.com/beta/deviceManagement/"
                    "configurationPolicies/policy-id/assignments"
                ),
                "value": [
                    {
                        "id": "assignment-id",
                        "sourceId": "policy-id",
                        "target": {
                            "@odata.type": "#microsoft.graph.groupAssignmentTarget",
                            "groupId": "group-id",
                            "groupName": "Test Group",
                            "groupType": "StaticMembership",
                        },
                    }
                ],
            }
        ]

        backup_assignment = self.module.get_object_assignment("policy-id", responses)
        update_assignment = self.module.get_object_assignment(
            "policy-id", responses, preserve_group_id=True
        )

        self.assertNotIn("groupId", backup_assignment[0]["target"])
        self.assertEqual(backup_assignment[0]["target"]["groupName"], "Test Group")
        self.assertEqual(update_assignment[0]["target"]["groupId"], "group-id")
        self.assertNotIn("groupName", update_assignment[0]["target"])

    @patch.object(BaseGraphModule, "log")
    def test_update_assignment_returns_repo_data_for_removal_only_diff(self, mock_log):
        repo_data = [
            {
                "intent": "Include",
                "target": {
                    "@odata.type": "#microsoft.graph.allDevicesAssignmentTarget"
                },
            }
        ]
        intune_data = [
            {
                "intent": "Include",
                "target": {
                    "@odata.type": "#microsoft.graph.allDevicesAssignmentTarget"
                },
            },
            {
                "intent": "Exclude",
                "target": {
                    "@odata.type": "#microsoft.graph.groupAssignmentTarget",
                    "groupId": "removed-group-id",
                },
            },
        ]

        result = self.module.update_assignment(repo_data, intune_data, False)

        self.assertIs(result, repo_data)
        mock_log.assert_any_call(msg="Updating assignments")
        mock_log.assert_any_call(msg="Removed assignments:")

    @patch.object(BaseGraphModule, "log")
    def test_update_assignment_returns_empty_repo_data_when_all_assignments_removed(
        self, mock_log
    ):
        repo_data = []
        intune_data = [
            {
                "intent": "Exclude",
                "target": {
                    "@odata.type": "#microsoft.graph.exclusionGroupAssignmentTarget",
                    "groupId": "removed-group-id",
                },
            }
        ]

        result = self.module.update_assignment(repo_data, intune_data, False)

        self.assertIs(result, repo_data)
        mock_log.assert_any_call(msg="Updating assignments")
        mock_log.assert_any_call(msg="Removed assignments:")
        mock_log.assert_any_call(
            msg="intent: Exclude, Filter ID: , Filter Type: , "
            "target: removed-group-id"
        )

    @patch.object(BaseGraphModule, "log")
    def test_update_assignment_returns_repo_data_for_assignment_type_change(
        self, mock_log
    ):
        repo_data = [
            {
                "intent": "Include",
                "target": {
                    "@odata.type": "#microsoft.graph.allDevicesAssignmentTarget"
                },
            }
        ]
        intune_data = [
            {
                "intent": "Include",
                "target": {
                    "@odata.type": "#microsoft.graph.groupAssignmentTarget",
                    "groupId": "old-group-id",
                },
            }
        ]

        result = self.module.update_assignment(repo_data, intune_data, False)

        self.assertIs(result, repo_data)
        mock_log.assert_any_call(msg="Updating assignments")
        mock_log.assert_any_call(msg="Changed assignments detected")

    @patch.object(BaseGraphModule, "make_graph_request")
    def test_update_assignment_ignores_same_group_after_group_name_resolution(
        self, mock_make_graph_request
    ):
        repo_data = [
            {
                "intent": "Include",
                "target": {
                    "@odata.type": "#microsoft.graph.groupAssignmentTarget",
                    "groupName": "Test Group",
                    "groupType": "StaticMembership",
                },
            }
        ]
        intune_data = [
            {
                "intent": "Include",
                "target": {
                    "@odata.type": "#microsoft.graph.groupAssignmentTarget",
                    "groupId": "group-id",
                },
            }
        ]
        mock_make_graph_request.return_value = {"value": [{"id": "group-id"}]}

        result = self.module.update_assignment(repo_data, intune_data, False)

        self.assertIsNone(result)
        self.assertEqual(repo_data[0]["target"]["groupId"], "group-id")
        self.assertNotIn("groupName", repo_data[0]["target"])


if __name__ == "__main__":
    unittest.main()
