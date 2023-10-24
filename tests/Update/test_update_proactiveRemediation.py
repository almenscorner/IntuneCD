#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests updating Proactive Remediation."""

import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.update_proactiveRemediation import update


class TestUpdateProactiveRemediation(unittest.TestCase):
    """Test class for update_proactiveRemediation."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Proactive Remediations")
        self.directory.makedir("Proactive Remediations/Script Data")
        self.directory.write(
            "Proactive Remediations/test.json", '{"test": "test"}', encoding="utf-8"
        )
        self.directory.write(
            "Proactive Remediations/Script Data/test_DetectionScript.ps1",
            "You found a secret message, hooray!",
            encoding="utf-8",
        )
        self.directory.write(
            "Proactive Remediations/Script Data/test_RemediationScript.ps1",
            "You found a secret message, hooray!",
            encoding="utf-8",
        )
        self.token = "token"
        self.script_content = "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2UsIGhvb3JheSE="
        self.mem_remediationScript_data = {
            "value": [
                {
                    "@odata.type": "test",
                    "id": "0",
                    "displayName": "test",
                    "testvalue": "test",
                    "detectionScriptContent": self.script_content,
                    "remediationScriptContent": self.script_content,
                    "fileName": "test.ps1",
                    "assignments": [{"target": {"groupId": "test"}}],
                }
            ]
        }
        self.mem_data = {
            "@odata.type": "test",
            "id": "0",
            "displayName": "test",
            "testvalue": "test",
            "detectionScriptContent": self.script_content,
            "remediationScriptContent": self.script_content,
            "fileName": "test.ps1",
            "assignments": [{"target": {"groupId": "test"}}],
        }
        self.repo_data = {
            "@odata.type": "test",
            "id": "0",
            "displayName": "test",
            "testvalue": "test",
            "detectionScriptContent": self.script_content,
            "remediationScriptContent": self.script_content,
            "fileName": "test.ps1",
            "assignments": [{"target": {"groupId": "test"}}],
        }

        self.batch_assignment_patch = patch(
            "src.IntuneCD.update.update_proactiveRemediation.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()

        self.object_assignment_patch = patch(
            "src.IntuneCD.update.update_proactiveRemediation.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.update_proactiveRemediation.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.update_assignment_patch = patch(
            "src.IntuneCD.update.update_proactiveRemediation.update_assignment"
        )
        self.update_assignment = self.update_assignment_patch.start()

        self.load_file_patch = patch(
            "src.IntuneCD.update.update_proactiveRemediation.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.post_assignment_update_patch = patch(
            "src.IntuneCD.update.update_proactiveRemediation.post_assignment_update"
        )
        self.post_assignment_update = self.post_assignment_update_patch.start()

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.update_proactiveRemediation.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update.update_proactiveRemediation.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update.update_proactiveRemediation.makeapirequestDelete"
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
        self.makeapirequest.side_effect = [
            self.mem_remediationScript_data,
            self.mem_data,
        ]

        self.count = update(
            self.directory.path, self.token, assignment=True, report=False, remove=False
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_detection_script_diff_and_assignment(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.mem_data[
            "detectionScriptContent"
        ] = "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2UsIGhvb3JheQ=="
        self.makeapirequest.side_effect = [
            self.mem_remediationScript_data,
            self.mem_data,
        ]

        self.count = update(
            self.directory.path, self.token, assignment=True, report=False, remove=False
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_detection_script_diff_no_assignment(self):
        """The count should be 1 and the makeapirequestPatch should be called."""

        self.mem_data[
            "detectionScriptContent"
        ] = "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2UsIGhvb3JheQ=="
        self.makeapirequest.side_effect = [
            self.mem_remediationScript_data,
            self.mem_data,
        ]

        self.count = update(
            self.directory.path,
            self.token,
            assignment=False,
            report=False,
            remove=False,
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_with_remediation_script_diff_and_assignment(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.mem_data[
            "remediationScriptContent"
        ] = "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2UsIGhvb3JheQ=="
        self.makeapirequest.side_effect = [
            self.mem_remediationScript_data,
            self.mem_data,
        ]

        self.count = update(
            self.directory.path, self.token, assignment=True, report=False, remove=False
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_remediation_script_diff_no_assignment(self):
        """The count should be 1 and the makeapirequestPatch should be called."""

        self.mem_data[
            "remediationScriptContent"
        ] = "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2UsIGhvb3JheQ=="
        self.makeapirequest.side_effect = [
            self.mem_remediationScript_data,
            self.mem_data,
        ]

        self.count = update(
            self.directory.path,
            self.token,
            assignment=False,
            report=False,
            remove=False,
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_with_diffs_no_assignment(self):
        """The count should be 1 and the makeapirequestPatch should be called."""

        self.repo_data["testvalue"] = "test1"
        self.makeapirequest.side_effect = [
            self.mem_remediationScript_data,
            self.mem_data,
        ]

        self.count = update(
            self.directory.path,
            self.token,
            assignment=False,
            report=False,
            remove=False,
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_with_no_diffs_and_assignment(self):
        """The count should be 0, the post_assignment_update should be called,
        and makeapirequestPatch should not be called."""

        self.repo_data["testvalue"] = "test"
        self.makeapirequest.side_effect = [
            self.mem_remediationScript_data,
            self.mem_data,
        ]

        self.count = update(
            self.directory.path, self.token, assignment=True, report=False, remove=False
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_no_diffs_no_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.mem_data["testvalue"] = "test"
        self.makeapirequest.side_effect = [
            self.mem_remediationScript_data,
            self.mem_data,
        ]

        self.count = update(
            self.directory.path,
            self.token,
            assignment=False,
            report=False,
            remove=False,
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_config_not_found_and_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.mem_remediationScript_data["value"][0]["displayName"] = "test1"
        self.makeapirequest.return_value = self.mem_remediationScript_data

        self.count = update(
            self.directory.path, self.token, assignment=True, report=False, remove=False
        )

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_remove_config(self):
        """makeapirequestDelete should be called."""

        self.mem_remediationScript_data["value"].append(
            {"displayName": "test2", "id": "2"}
        )
        self.makeapirequest.side_effect = [
            self.mem_remediationScript_data,
            self.mem_data,
        ]

        self.update = update(self.directory.path, self.token, report=False, remove=True)

        self.assertEqual(self.makeapirequestDelete.call_count, 1)


if __name__ == "__main__":
    unittest.main()
