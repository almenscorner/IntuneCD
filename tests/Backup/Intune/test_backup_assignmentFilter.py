#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up assignment filters."""

import json
import os.path
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.Intune.backup_assignmentFilters import savebackup


class TestBackupAssignmentFilters(unittest.TestCase):
    """Test class for backup_assignmentFilters."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.append_id = False
        self.saved_path = f"{self.directory.path}/Filters/macOS - Model."
        self.expected_data = {
            "displayName": "macOS - Model",
            "description": "",
            "platform": "macOS",
            "rule": '(device.model -eq "macbook Pro")',
            "roleScopeTags": ["0"],
        }
        self.assignment_filter = {
            "value": [
                {
                    "displayName": "macOS - Model",
                    "description": "",
                    "id": "0",
                    "platform": "macOS",
                    "rule": '(device.model -eq "macbook Pro")',
                    "roleScopeTags": ["0"],
                }
            ]
        }
        self.audit_data = {
            "value": [
                {
                    "resources": [
                        {"resourceId": "0", "auditResourceType": "MagicResource"}
                    ],
                    "activityDateTime": "2021-01-01T00:00:00Z",
                    "activityOperationType": "Patch",
                    "activityResult": "Success",
                    "actor": [{"auditActorType": "ItPro"}],
                }
            ]
        }

        self.patch_makeapirequest = patch(
            "src.IntuneCD.backup.Intune.backup_assignmentFilters.makeapirequest",
            return_value=self.assignment_filter,
        )
        self.makeapirequest = self.patch_makeapirequest.start()

        self.makeAuditRequest = patch(
            "src.IntuneCD.backup.Intune.backup_assignmentFilters.makeAuditRequest",
            return_value=self.audit_data,
        )
        self.makeAuditRequest = self.makeAuditRequest.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest.stop()
        self.makeAuditRequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "yaml", self.token, "", self.append_id, False, ""
        )

        with open(self.saved_path + "yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(Path(f"{self.directory.path}/Filters").exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", self.token, "", self.append_id, False, ""
        )

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            self.saved_data = json.load(f)

        self.assertTrue(Path(f"{self.directory.path}/Filters").exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_return_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = {"value": []}
        self.count = savebackup(
            self.directory.path, "json", self.token, "", self.append_id, False, ""
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if no data is returned."""

        self.assignment_filter["value"][0]["displayName"] = "test1 - macos model"
        self.count = savebackup(
            self.directory.path, "json", self.token, "test1", True, False, ""
        )
        self.assertEqual(1, self.count["config_count"])
        self.assertTrue(
            os.path.exists(f"{self.directory.path}/Filters/test1 - macos model__0.json")
        )

    def test_backup_with_prefix_no_match(self):
        """The count should be 0 if no data is returned."""

        self.count = savebackup(
            self.directory.path, "json", self.token, "test1", True, False, ""
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_append_id(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", self.token, "", True, False, ""
        )

        self.assertTrue(
            Path(f"{self.directory.path}/Filters/macOS - Model__0.json").exists()
        )

    def test_backup_scope_tag_and_audit(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""
        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            "",
            True,
            True,
            [{"id": 0, "displayName": "default"}],
        )
        self.assertTrue(
            Path(f"{self.directory.path}/Filters/macOS - Model__0.json").exists()
        )
        self.assertEqual(1, self.count["config_count"])


if __name__ == "__main__":
    unittest.main()
