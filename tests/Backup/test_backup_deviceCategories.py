#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up deviceCategories."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.backup_deviceCategories import savebackup


class TestBackupdeviceCategories(unittest.TestCase):
    """Test class for backup_deviceCategories."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.append_id = False
        self.saved_path = f"{self.directory.path}/Device Categories/Test."
        self.expected_data = {
            "displayName": "Test",
            "description": "Test",
            "roleScopeTagIds": [],
        }
        self.deviceCategories = {
            "value": [
                {
                    "@odata.context": "test",
                    "id": "00000000-0000-0000-0000-000000000000",
                    "displayName": "Test",
                    "description": "Test",
                    "roleScopeTagIds": [],
                }
            ]
        }

        self.patch_makeapirequest = patch(
            "src.IntuneCD.backup.backup_deviceCategories.makeapirequest",
            return_value=self.deviceCategories,
        )
        self.makeapirequest = self.patch_makeapirequest.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "yaml", self.token, "", self.append_id
        )

        with open(self.saved_path + "yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(Path(f"{self.directory.path}/Device Categories").exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", self.token, "", self.append_id
        )

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertTrue(Path(f"{self.directory.path}/Device Categories").exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_return_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = {"value": []}
        self.count = savebackup(
            self.directory.path, "json", self.token, "", self.append_id
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = {"value": []}
        self.count = savebackup(
            self.directory.path, "json", self.token, "test", self.append_id
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_append_id(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "json", self.token, "", True)

        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Categories/Test__00000000-0000-0000-0000-000000000000.json"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
