#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up Roles."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.Intune.backup_roles import savebackup


class TestBackupRoles(unittest.TestCase):
    """Test class for backup_roles."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.append_id = False
        self.saved_path = f"{self.directory.path}/Roles/test."
        self.expected_data = {
            "@odata.type": "#microsoft.graph.deviceAndAppManagementRoleDefinition",
            "displayName": "test",
            "description": "test.",
            "isBuiltInRoleDefinition": True,
            "isBuiltIn": True,
            "roleScopeTagIds": [],
            "permissions": [
                {
                    "actions": ["test"],
                    "resourceActions": ["test"],
                }
            ],
            "roleAssignments": [
                {"id": "test", "roleAssignments": {"displayName": "test", "id": "test"}}
            ],
        }
        self.role = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.deviceAndAppManagementRoleDefinition",
                    "id": "0",
                    "displayName": "test",
                    "description": "test.",
                    "isBuiltInRoleDefinition": True,
                    "isBuiltIn": True,
                    "roleScopeTagIds": [],
                    "permissions": [
                        {
                            "actions": ["test"],
                            "resourceActions": ["test"],
                        }
                    ],
                }
            ]
        }
        self.assignment = {
            "value": [
                {
                    "id": "test",
                    "roleAssignments": {
                        "id": "test",
                        "displayName": "test",
                    },
                }
            ]
        }

        self.patch_makeapirequest = patch(
            "src.IntuneCD.backup.Intune.backup_roles.makeapirequest",
            side_effect=[self.role, self.assignment, self.assignment["value"][0]],
        )
        self.makeapirequest = self.patch_makeapirequest.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "yaml", "", self.token, self.append_id
        )

        with open(self.saved_path + "yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(Path(f"{self.directory.path}/Roles").exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", "", self.token, self.append_id
        )

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            self.saved_data = json.load(f)

        self.assertTrue(Path(f"{self.directory.path}/Roles").exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_return_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.side_effect = [{"value": []}, {"value": []}, {"value": []}]
        self.count = savebackup(
            self.directory.path, "json", "", self.token, self.append_id
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_append_id(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "json", "", self.token, True)

        self.assertTrue(Path(f"{self.directory.path}/Roles/test__0.json").exists())


if __name__ == "__main__":
    unittest.main()
