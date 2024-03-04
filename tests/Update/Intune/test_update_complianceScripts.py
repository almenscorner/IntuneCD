#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests updating Compliance Scripts."""

import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Intune.update_complianceScripts import update


@patch("time.sleep", return_value=None)
class TestUpdateComplianceScripts(unittest.TestCase):
    """Test class for update_complianceScripts."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Compliance Policies/Scripts")
        self.directory.makedir("Compliance Policies/Scripts/Script Data")
        self.directory.write(
            "Compliance Policies/Scripts/test.json",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.directory.write(
            "Compliance Policies/Scripts/Script Data/test.sh",
            "You found a secret message, hooray!",
            encoding="utf-8",
        )
        self.token = "token"
        self.mem_script_content = "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2Us"
        self.repo_script_content = "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2UsIGhvb3JheSE="
        self.mem_detectionScript_data = {
            "value": [
                {
                    "@odata.type": "test",
                    "id": "0",
                    "displayName": "test",
                    "testvalue": "test",
                    "detectionScriptContent": self.mem_script_content,
                }
            ]
        }
        self.mem_data = {
            "@odata.type": "test",
            "id": "0",
            "displayName": "test",
            "testvalue": "test",
            "detectionScriptContent": self.mem_script_content,
        }
        self.repo_data = {
            "@odata.type": "test",
            "id": "0",
            "displayName": "test",
            "testvalue": "test",
            "detectionScriptContent": self.repo_script_content,
        }

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Intune.update_complianceScripts.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.load_file_patch = patch(
            "src.IntuneCD.update.Intune.update_complianceScripts.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Intune.update_complianceScripts.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update.Intune.update_complianceScripts.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update.Intune.update_complianceScripts.makeapirequestDelete"
        )
        self.makeapirequestDelete = self.makeapirequestDelete_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest.stop()
        self.load_file.stop()
        self.makeapirequestPatch.stop()
        self.makeapirequestPost.stop()
        self.makeapirequestDelete.stop()

    def test_update_with_diffs(self, _):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_data["testvalue"] = "test1"
        self.makeapirequest.side_effect = [self.mem_detectionScript_data, self.mem_data]

        self.count = update(
            self.directory.path, self.token, report=False, remove=False, scope_tags=""
        )

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)

    def test_update_with_no_diffs(self, _):
        """The count should be 0, the post_assignment_update should be called,
        and makeapirequestPatch should not be called."""

        self.mem_data["testvalue"] = "test"
        self.mem_data["detectionScriptContent"] = self.repo_script_content

        self.makeapirequest.side_effect = [self.mem_detectionScript_data, self.mem_data]

        self.count = update(
            self.directory.path, self.token, report=False, remove=False, scope_tags=""
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)

    def test_update_config_not_found(self, _):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.mem_detectionScript_data["value"][0]["displayName"] = "test1"
        self.makeapirequest.return_value = self.mem_detectionScript_data

        self.count = update(
            self.directory.path, self.token, report=False, remove=False, scope_tags=""
        )

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)

    def test_remove_config(self, _):
        """makeapirequestDelete should be called."""

        self.mem_detectionScript_data["value"].append(
            {"displayName": "test2", "id": "2"}
        )
        self.makeapirequest.side_effect = [self.mem_detectionScript_data, self.mem_data]

        self.update = update(
            self.directory.path, self.token, report=False, remove=True, scope_tags=""
        )

        self.assertEqual(self.makeapirequestDelete.call_count, 1)

    def test_update_scope_tags(self, _):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_data["testvalue"] = "test1"
        self.makeapirequest.side_effect = [self.mem_detectionScript_data, self.mem_data]

        self.count = update(
            self.directory.path,
            self.token,
            remove=False,
            scope_tags=["test"],
        )

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)

    def test_update_settingDefinitionId(self, _):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_data["settingDefinitionId"] = "test"
        self.makeapirequest.side_effect = [self.mem_detectionScript_data, self.mem_data]

        self.count = update(
            self.directory.path, self.token, report=False, remove=False, scope_tags=""
        )

        self.assertEqual(self.count, [])


if __name__ == "__main__":
    unittest.main()
