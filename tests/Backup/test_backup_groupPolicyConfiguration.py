#!/usr/bin/env python3

"""This module tests backing up Group Policy Configurations."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from src.IntuneCD.backup_groupPolicyConfiguration import savebackup
from testfixtures import TempDirectory

BATCH_ASSIGNMENT = [{"value": [{"id": "0", "target": {"groupName": "Group1"}}]}]
OBJECT_ASSIGNMENT = [{"target": {"groupName": "Group1"}}]


class TestBackupGroupPolicyConfiguration(unittest.TestCase):
    """Test class for backup_groupPolicyConfiguration."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.saved_path = f"{self.directory.path}/Group Policy Configurations/test."
        self.expected_data = {
            "assignments": [{"target": {"groupName": "Group1"}}],
            "definitionValues": [
                {
                    "classType": "machine",
                    "displayName": "Default search provider icon",
                    "id": "0",
                    "policyType": "admxIngested",
                    "presentationValues": [],
                    "version": "1.0",
                }
            ],
            "description": "",
            "displayName": "test",
            "roleScopeTagIds": ["0"],
        }
        self.group_policy = {
            "value": [
                {
                    "displayName": "test",
                    "description": "",
                    "id": "0",
                    "roleScopeTagIds": ["0"],
                }
            ]
        }
        self.definitions = {
            "value": [
                {
                    "classType": "machine",
                    "displayName": "Default search provider icon",
                    "policyType": "admxIngested",
                    "version": "1.0",
                    "id": "0",
                }
            ]
        }
        self.presentations = {"value": []}

        self.batch_assignment_patch = patch(
            "src.IntuneCD.backup_groupPolicyConfiguration.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup_groupPolicyConfiguration.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup_groupPolicyConfiguration.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.side_effect = (
            self.group_policy,
            self.definitions,
            self.presentations,
        )

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "yaml", self.exclude, self.token, ""
        )

        with open(self.saved_path + "yaml", "r") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(
            Path(f"{self.directory.path}/Group Policy Configurations").exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, ""
        )

        with open(self.saved_path + "json", "r") as f:
            saved_data = json.load(f)

        self.assertTrue(
            Path(f"{self.directory.path}/Group Policy Configurations").exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_returned_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.side_effect = [{"value": []}]
        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, ""
        )

        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if no data is returned."""

        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, "test1"
        )
        self.assertEqual(0, self.count["config_count"])


if __name__ == "__main__":
    unittest.main()
