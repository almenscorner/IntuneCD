#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests updating Custom Attribute Shell Scripts."""

import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.update_customAttributeShellScript import update


class TestUpdatecustomAttributeShellScripts(unittest.TestCase):
    """Test class for update_customAttributeShellScript."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Custom Attributes")
        self.directory.makedir("Custom Attributes/Script Data")
        self.directory.write(
            "Custom Attributes/test.json", '{"test": "test"}', encoding="utf-8"
        )
        self.directory.write(
            "Custom Attributes/Script Data/test.sh",
            "You found a secret message, hooray!",
            encoding="utf-8",
        )
        self.token = "token"
        self.mem_script_content = "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2Us"
        self.repo_script_content = "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2UsIGhvb3JheSE="
        self.mem_shellScript_data = {
            "value": [
                {
                    "@odata.type": "test",
                    "id": "0",
                    "displayName": "test",
                    "testvalue": "test",
                    "scriptContent": self.mem_script_content,
                    "fileName": "test.sh",
                    "assignments": [{"target": {"groupId": "test"}}],
                }
            ]
        }
        self.mem_data = {
            "@odata.type": "test",
            "id": "0",
            "displayName": "test",
            "testvalue": "test",
            "scriptContent": self.mem_script_content,
            "fileName": "test.sh",
            "assignments": [{"target": {"groupId": "test"}}],
        }
        self.repo_data = {
            "@odata.type": "test",
            "id": "0",
            "displayName": "test",
            "testvalue": "test",
            "scriptContent": self.repo_script_content,
            "fileName": "test.sh",
            "assignments": [{"target": {"groupId": "test"}}],
        }

        self.batch_assignment_patch = patch(
            "src.IntuneCD.update.update_customAttributeShellScript.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()

        self.object_assignment_patch = patch(
            "src.IntuneCD.update.update_customAttributeShellScript.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.update_customAttributeShellScript.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.update_assignment_patch = patch(
            "src.IntuneCD.update.update_customAttributeShellScript.update_assignment"
        )
        self.update_assignment = self.update_assignment_patch.start()

        self.load_file_patch = patch(
            "src.IntuneCD.update.update_customAttributeShellScript.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.post_assignment_update_patch = patch(
            "src.IntuneCD.update.update_customAttributeShellScript.post_assignment_update"
        )
        self.post_assignment_update = self.post_assignment_update_patch.start()

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.update_customAttributeShellScript.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update.update_customAttributeShellScript.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update.update_customAttributeShellScript.makeapirequestDelete"
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
        self.makeapirequestPatch.stop()
        self.makeapirequestPost.stop()
        self.makeapirequestDelete.stop()

    def test_update_with_diffs_and_assignment(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_data["testvalue"] = "test1"
        self.makeapirequest.side_effect = [self.mem_shellScript_data, self.mem_data]

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_diffs_no_assignment(self):
        """The count should be 1 and the makeapirequestPatch should be called."""

        self.repo_data["testvalue"] = "test1"
        self.makeapirequest.side_effect = [self.mem_shellScript_data, self.mem_data]

        self.count = update(
            self.directory.path, self.token, assignment=False, remove=False
        )

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_with_no_diffs_and_assignment(self):
        """The count should be 0, the post_assignment_update should be called,
        and makeapirequestPatch should not be called."""

        self.mem_data["testvalue"] = "test"
        self.mem_data["scriptContent"] = self.repo_script_content

        self.makeapirequest.side_effect = [self.mem_shellScript_data, self.mem_data]

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_no_diffs_no_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.mem_data["testvalue"] = "test"
        self.mem_data["scriptContent"] = self.repo_script_content

        self.makeapirequest.side_effect = [self.mem_shellScript_data, self.mem_data]

        self.count = update(
            self.directory.path, self.token, assignment=False, remove=False
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_config_not_found_and_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.mem_shellScript_data["value"][0]["displayName"] = "test1"
        self.makeapirequest.return_value = self.mem_shellScript_data

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_remove_config(self):
        """makeapirequestDelete should be called."""

        self.mem_shellScript_data["value"].append({"displayName": "test2", "id": "2"})

        self.makeapirequest.side_effect = [self.mem_shellScript_data, self.mem_data]

        self.update = update(self.directory.path, self.token, report=False, remove=True)

        self.assertEqual(self.makeapirequestDelete.call_count, 1)


if __name__ == "__main__":
    unittest.main()
