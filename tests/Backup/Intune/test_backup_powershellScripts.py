#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up Powershell Scripts."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.Intune.backup_powershellScripts import savebackup

BATCH_ASSIGNMENT = [{"value": [{"id": "0", "target": {"groupName": "Group1"}}]}]
OBJECT_ASSIGNMENT = [{"target": {"groupName": "Group1"}}]


class TestBackupPowershellScript(unittest.TestCase):
    """Test class for backup_powershellScript."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.append_id = False
        self.saved_path = f"{self.directory.path}/Scripts/Powershell/test."
        self.script_content_path = (
            f"{self.directory.path}/Scripts/Powershell/Script Data/test.ps1"
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
            "src.IntuneCD.backup.Intune.backup_powershellScripts.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup.Intune.backup_powershellScripts.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.batch_request_patch = patch(
            "src.IntuneCD.backup.Intune.backup_powershellScripts.batch_request"
        )
        self.batch_request = self.batch_request_patch.start()
        self.batch_request.return_value = self.batch_request_data

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_powershellScripts.makeapirequest"
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

        self.count = savebackup(
            self.directory.path, "yaml", self.exclude, self.token, "", self.append_id
        )

        with open(self.saved_path + "yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(Path(f"{self.directory.path}/Scripts/Powershell").exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, "", self.append_id
        )

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            self.saved_data = json.load(f)

        self.assertTrue(Path(f"{self.directory.path}/Scripts/Powershell").exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_script_is_created(self):
        """The script data folder should be created and a .ps1 file should be created."""

        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, "", self.append_id
        )

        self.assertTrue(
            Path(f"{self.directory.path}/Scripts/Powershell/Script Data").exists()
        )
        self.assertTrue(self.script_content_path)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_returned_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = {"value": []}
        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, "", self.append_id
        )

        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if no data is returned."""

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            "test1",
            self.append_id,
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_append_id(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, "", True
        )

        self.assertTrue(
            Path(f"{self.directory.path}/Scripts/Powershell/test__0.json").exists()
        )
        self.assertTrue(
            Path(
                f"{self.directory.path}/Scripts/Powershell/Script Data/test__0.ps1"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
