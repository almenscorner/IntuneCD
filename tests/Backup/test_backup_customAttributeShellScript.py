#!/usr/bin/env python3

"""This module tests backing up Shell Scripts."""

import json
import yaml
import unittest

from unittest.mock import patch
from testfixtures import TempDirectory
from src.IntuneCD.backup_customAttributeShellScript import savebackup

BATCH_ASSIGNMENT = [{"value": [{"id": "0", "target": {"groupName": "Group1"}}]}]
OBJECT_ASSIGNMENT = [{"target": {"groupName": "Group1"}}]


class TestBackupCustomAttributeShellScript(unittest.TestCase):
    """Test class for backup_customAttributeShellScript."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.saved_path = f"{self.directory.path}/Custom Attributes/test."
        self.script_content_path = (
            f"{self.directory.path}/Custom Attributes/Script Data/test.ps1"
        )
        self.expected_data = {
            "assignments": [{"target": {"groupName": "Group1"}}],
            "displayName": "test",
            "fileName": "test",
            "scriptContent": "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2UsIGhvb3JheSE=",
        }
        self.script_policy_data = {"value": [{"id": "0", "displayName": "test"}]}
        self.batch_request_data = [
            {
                "id": "0",
                "displayName": "test",
                "fileName": "test",
                "scriptContent": "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2UsIGhvb3JheSE=",
            }
        ]

        self.batch_assignment_patch = patch(
            "src.IntuneCD.backup_customAttributeShellScript.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup_customAttributeShellScript.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.batch_request_patch = patch(
            "src.IntuneCD.backup_customAttributeShellScript.batch_request"
        )
        self.batch_request = self.batch_request_patch.start()
        self.batch_request.return_value = self.batch_request_data

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup_customAttributeShellScript.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.script_policy_data

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.batch_request.stop()
        self.makeapirequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "yaml", self.exclude, self.token)

        with open(self.saved_path + "yaml", "r") as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(f"{self.directory.path}/Custom Attributes")
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count)

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "json", self.exclude, self.token)

        with open(self.saved_path + "json", "r") as f:
            self.saved_data = json.load(f)

        self.assertTrue(f"{self.directory.path}/Custom Attributes")
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count)

    def test_script_is_created(self):
        """The folder should be created and a .ps1 file should be created."""

        self.count = savebackup(self.directory.path, "json", self.exclude, self.token)

        self.assertTrue(f"{self.directory.path}/Custom Attributes/Script Data")
        self.assertTrue(self.script_content_path)
        self.assertEqual(1, self.count)

    def test_backup_with_no_returned_data(self):
        """The count should be 0 if no data is returned."""

        self.batch_request.return_value = []
        self.count = savebackup(self.directory.path, "json", self.exclude, self.token)

        self.assertEqual(0, self.count)


if __name__ == "__main__":
    unittest.main()
