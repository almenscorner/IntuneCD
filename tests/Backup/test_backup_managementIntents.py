#!/usr/bin/env python3

"""This module tests backing up Management Intents."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from src.IntuneCD.backup_managementIntents import savebackup
from testfixtures import TempDirectory

BATCH_ASSIGNMENT = [{"value": [{"id": "0", "target": {"groupName": "Group1"}}]}]
OBJECT_ASSIGNMENT = [{"target": {"groupName": "Group1"}}]


class TestBackupManagementIntent(unittest.TestCase):
    """Test class for backup_managementIntent."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.saved_path = f"{self.directory.path}/Management Intents/Dummy Intent/test."
        self.expected_data = {
            "assignments": [{"target": {"groupName": "Group1"}}],
            "description": "Hi there",
            "displayName": "test",
            "templateId": "0",
            "roleScopeTagIds": ["0"],
            "settingsDelta": [{"value": True}],
        }
        self.intent = {
            "value": [
                {
                    "displayName": "test",
                    "id": "0",
                }
            ]
        }
        self.template = {
            "value": [
                {
                    "displayName": "Dummy Intent",
                    "id": "0",
                }
            ]
        }
        self.batch_intent_data = {
            "value": [
                {
                    "id": "0",
                    "displayName": "test",
                    "description": "Hi there",
                    "templateId": "0",
                    "settingsDelta": [{"value": True}],
                    "roleScopeTagIds": ["0"],
                }
            ]
        }

        self.batch_intent_patch = patch(
            "src.IntuneCD.backup_managementIntents.batch_intents"
        )
        self.batch_intent = self.batch_intent_patch.start()
        self.batch_intent.return_value = self.batch_intent_data

        self.batch_assignment_patch = patch(
            "src.IntuneCD.backup_managementIntents.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup_managementIntents.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup_managementIntents.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.side_effect = self.intent, self.template

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()
        self.batch_intent.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "yaml", self.exclude, self.token, ""
        )

        with open(self.saved_path + "yaml", "r") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(
            Path(f"{self.directory.path}/Management Intents/Dummy Intent").exists()
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
            Path(f"{self.directory.path}/Management Intents/Dummy Intent").exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_returned_data(self):
        """The count should be 0 if no data is returned."""

        self.batch_intent.return_value = {"value": []}
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
