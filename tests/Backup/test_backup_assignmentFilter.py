#!/usr/bin/env python3

"""This module tests backing up assignment filters."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from testfixtures import TempDirectory
from src.IntuneCD.backup_assignmentFilters import savebackup


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

        self.patch_makeapirequest = patch(
            "src.IntuneCD.backup_assignmentFilters.makeapirequest",
            return_value=self.assignment_filter,
        )
        self.makeapirequest = self.patch_makeapirequest.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "yaml", self.token, "", self.append_id)

        with open(self.saved_path + "yaml", "r") as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(Path(f"{self.directory.path}/Filters").exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "json", self.token, "", self.append_id)

        with open(self.saved_path + "json", "r") as f:
            self.saved_data = json.load(f)

        self.assertTrue(Path(f"{self.directory.path}/Filters").exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_return_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = {"value": []}
        self.count = savebackup(self.directory.path, "json", self.token, "", self.append_id)
        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = {"value": []}
        self.count = savebackup(self.directory.path, "json", self.token, "test", self.append_id)
        self.assertEqual(0, self.count["config_count"])

    def test_backup_append_id(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "json", self.token, "", True)

        self.assertTrue(Path(f"{self.directory.path}/Filters/macOS - Model__0.json").exists())


if __name__ == "__main__":
    unittest.main()
