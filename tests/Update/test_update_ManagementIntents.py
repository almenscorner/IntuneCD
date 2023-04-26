#!/usr/bin/env python3

"""This module tests updating Management Intents."""

import unittest

from testfixtures import TempDirectory
from unittest.mock import patch
from src.IntuneCD.update_managementIntents import update


class TestUpdateManagementIntents(unittest.TestCase):
    """Test class for update_managementIntents."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Management Intents")
        self.directory.write(
            "Management Intents/macOS Firewall/test.json",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.directory.write(
            "Management Intents/macOS Firewall/.DS_Store", "", encoding="utf-8"
        )
        self.directory.write(
            "Management Intents/macOS Firewall/test.md", "", encoding="utf-8"
        )
        self.token = "token"
        self.mem_data = {
            "value": [
                {
                    "@odata.type": "test",
                    "id": "0",
                    "displayName": "test",
                    "assignments": [{"target": {"groupId": "test"}}],
                }
            ]
        }
        self.repo_data = {
            "id": "0",
            "displayName": "test",
            "description": "Hi there",
            "templateId": "0",
            "settingsDelta": [
                {
                    "@odata.type": "#test.test",
                    "definitionId": "test_test",
                    "value": False,
                }
            ],
            "assignments": [{"target": {"groupName": "test1"}}],
        }
        self.batch_intent_data = {
            "value": [
                {
                    "id": "0",
                    "displayName": "test",
                    "description": "Hi there",
                    "templateId": "0",
                    "settingsDelta": [
                        {
                            "id": "0",
                            "@odata.type": "#test.test",
                            "definitionId": "test_test",
                            "value": True,
                        }
                    ],
                }
            ]
        }

        self.batch_assignment_patch = patch(
            "src.IntuneCD.update_managementIntents.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()

        self.batch_intents_patch = patch(
            "src.IntuneCD.update_managementIntents.batch_intents"
        )
        self.batch_intents = self.batch_intents_patch.start()
        self.batch_intents.return_value = self.batch_intent_data

        self.object_assignment_patch = patch(
            "src.IntuneCD.update_managementIntents.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update_managementIntents.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.update_assignment_patch = patch(
            "src.IntuneCD.update_managementIntents.update_assignment"
        )
        self.update_assignment = self.update_assignment_patch.start()

        self.load_file_patch = patch("src.IntuneCD.update_managementIntents.load_file")
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.post_assignment_update_patch = patch(
            "src.IntuneCD.update_managementIntents.post_assignment_update"
        )
        self.post_assignment_update = self.post_assignment_update_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update_managementIntents.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update_managementIntents.makeapirequestDelete"
        )
        self.makeapirequestDelete = self.makeapirequestDelete_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()
        self.update_assignment.stop()
        self.load_file.stop()
        self.post_assignment_update.stop()
        self.batch_intents.stop()
        self.makeapirequestPost.stop()
        self.makeapirequestDelete.stop()

    def test_update_with_diffs_and_assignment(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPost should be called."""

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPost.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_diffs_no_assignment(self):
        """The count should be 1 and the makeapirequestPost should be called."""

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPost.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_with_no_diffs_and_assignment(self):
        """The count should be 0, the post_assignment_update should be called,
        and makeapirequestPost should not be called."""
        self.batch_intent_data["value"][0]["settingsDelta"][0]["value"] = False

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPost.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_no_diffs_no_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPost should not be called."""

        self.batch_intent_data["value"][0]["settingsDelta"][0]["value"] = False

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPost.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_config_not_found_and_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.mem_data["value"][0]["displayName"] = "test1"
        self.batch_intent_data["value"][0]["templateId"] = "test1_test1"

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_skip_edr(self):
        """The count should be 0 as EDR is currently not supported"""

        self.repo_data["templateId"] = "e44c2ca3-2f9a-400a-a113-6cc88efd773d"

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 0)


if __name__ == "__main__":
    unittest.main()
