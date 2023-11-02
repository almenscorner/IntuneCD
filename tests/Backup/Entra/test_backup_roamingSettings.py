#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up roamingSettings."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.Entra.backup_roamingSettings import savebackup


class TestBackupRoamingSettings(unittest.TestCase):
    """Test class for backup_roamingSettings."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.append_id = False
        self.saved_path = (
            f"{self.directory.path}/Entra/Roaming Settings/roaming_settings."
        )
        self.expected_data = {
            "syncSetting": 1,
            "isAdminConfigurable": True,
            "isRoamingSettingChanged": False,
            "syncSelectedUsers": [
                {
                    "id": "5279e130-ee8b-4b78-8b55-d18b774e676c",
                    "email": None,
                    "displayName": None,
                    "type": 2,
                    "hasThumbnail": False,
                    "imageUrl": None,
                }
            ],
        }
        self.roamingSettings = self.expected_data

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup.Entra.backup_roamingSettings.make_azure_request"
        )
        self.makeapirequest = self.makeapirequest_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest_patch.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.makeapirequest.return_value = self.roamingSettings
        self.count = savebackup(self.directory.path, "yaml", self.token)

        with open(self.saved_path + "yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(Path(f"{self.directory.path}/Entra/Roaming Settings").exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.makeapirequest.return_value = self.roamingSettings
        self.count = savebackup(self.directory.path, "json", self.token)

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertTrue(Path(f"{self.directory.path}/Entra/Roaming Settings").exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_return_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = None
        self.count = savebackup(self.directory.path, "json", self.token)
        self.assertEqual(0, self.count["config_count"])


if __name__ == "__main__":
    unittest.main()
