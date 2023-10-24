#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up App Protection."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup_AppProtection import savebackup

BATCH_ASSIGNMENT = [{"value": [{"id": "0", "target": {"groupName": "Group1"}}]}]
OBJECT_ASSIGNMENT = [{"target": {"groupName": "Group1"}}]


class TestBackupAppProtection(unittest.TestCase):
    """Test class for backup_appProtection."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.append_id = False
        self.saved_path = (
            f"{self.directory.path}/App Protection/test_iosManagedAppProtection."
        )
        self.saved_targetedAppManagementLevels = (
            f"{self.directory.path}/App Protection/test_test."
        )
        self.expected_data = {
            "@odata.type": "#microsoft.graph.iosManagedAppProtection",
            "displayName": "test",
            "description": "",
            "roleScopeTagIds": ["0"],
            "exemptedAppProtocols": [
                {
                    "name": "Default",
                    "value": "skype;app-settings;calshow;itms;itmss;itms-apps;itms-appss;itms-services;",
                }
            ],
            "assignments": [{"target": {"groupName": "Group1"}}],
        }
        self.app_protection = {
            "@odata.context": "https://graph.microsoft.com/beta/$metadata#deviceAppManagement/managedAppPolicies",
            "value": [
                {
                    "@odata.type": "#microsoft.graph.iosManagedAppProtection",
                    "displayName": "test",
                    "id": "T_0",
                    "description": "",
                    "roleScopeTagIds": ["0"],
                    "version": '"0"',
                    "exemptedAppProtocols": [
                        {
                            "name": "Default",
                            "value": "skype;app-settings;calshow;itms;itmss;itms-apps;itms-appss;itms-services;",
                        }
                    ],
                }
            ],
        }

        self.batch_assignment_patch = patch(
            "src.IntuneCD.backup_AppProtection.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup_AppProtection.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup_AppProtection.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.app_protection

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "yaml", self.exclude, self.token, "", self.append_id
        )

        with open(self.saved_path + "yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(Path(f"{self.directory.path}/App Protection").exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, "", self.append_id
        )

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            self.saved_data = json.load(f)

        self.assertTrue(Path(f"{self.directory.path}/App Protection").exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_targetedManagedAppConfiguration(self):
        """The count should be 0 since the targetedManagedAppConfiguration is not supported."""

        self.makeapirequest.return_value = {
            "value": [
                {"@odata.type": "#microsoft.graph.targetedManagedAppConfiguration"}
            ]
        }
        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, "", self.append_id
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_targetedAppManagementLevels(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.app_protection["value"][0]["targetedAppManagementLevels"] = "test"
        self.expected_data["targetedAppManagementLevels"] = "test"

        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, "", self.append_id
        )

        with open(
            self.saved_targetedAppManagementLevels + "json", "r", encoding="utf-8"
        ) as f:
            self.saved_data = json.load(f)

        self.assertTrue(Path(f"{self.directory.path}/App Protection").exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_returned_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = {"value": []}
        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, "", self.append_id
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if the prefix does not match."""

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
            Path(
                f"{self.directory.path}/App Protection/test_iosManagedAppProtection__T_0.json"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
