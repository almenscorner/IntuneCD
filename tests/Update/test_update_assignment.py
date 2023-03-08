import unittest

from unittest.mock import patch
from src.IntuneCD.update_assignment import (
    update_assignment,
    get_added_removed,
    post_assignment_update,
)


class TestUpdateAssignment(unittest.TestCase):
    """Test class for update_assignment."""

    def setUp(self):
        self.token = "token"
        self.output_data = {
            "assignments": {
                "intent": "apply",
                "target": {
                    "@odata.type": "#microsoft.graph.allDevicesAssignmentTarget",
                    "deviceAndAppManagementAssignmentFilterId": "1234",
                    "deviceAndAppManagementAssignmentFilterType": "device",
                },
            }
        }
        self.mem_data = []
        self.repo_data = [
            {
                "source": "direct",
                "intent": "apply",
                "target": {
                    "@odata.type": "#microsoft.graph.groupAssignmentTarget",
                    "deviceAndAppManagementAssignmentFilterId": "test",
                    "deviceAndAppManagementAssignmentFilterType": "device",
                    "groupName": "test",
                },
            }
        ]
        self.request_data = {"value": [{"id": "12345", "displayName": "test"}]}
        self.makeapirequest_patch = patch(
            "src.IntuneCD.update_assignment.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update_assignment.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()

    def tearDown(self):
        self.makeapirequest.stop()
        self.makeapirequestPost.stop()

    def test_get_added_removed(self):
        """The list of added and removed should be returned."""
        result = get_added_removed(self.output_data)

        self.assertEqual(
            result,
            [
                "intent: apply, Filter ID: 1234, Filter Type: device, target: All Devices"
            ],
        )

    def test_update_assignment(self):
        self.makeapirequest.return_value = self.request_data

        result = update_assignment(
            self.repo_data, self.mem_data, self.token, create_groups=True
        )

        self.assertEqual(
            result,
            [
                {
                    "source": "direct",
                    "intent": "apply",
                    "target": {
                        "@odata.type": "#microsoft.graph.groupAssignmentTarget",
                        "deviceAndAppManagementAssignmentFilterId": "12345",
                        "deviceAndAppManagementAssignmentFilterType": "device",
                        "groupId": "12345",
                    },
                }
            ],
        )

        self.assertEqual(self.makeapirequest.call_count, 2)
