#!/usr/bin/env python3

"""This module tests backing up compliance."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from testfixtures import TempDirectory
from src.IntuneCD.backup_compliance import savebackup

BATCH_ASSIGNMENT = [{"value": [{"id": "0", "target": {"groupName": "Group1"}}]}]
OBJECT_ASSIGNMENT = [{"target": {"groupName": "Group1"}}]


class TestBackupCompliance(unittest.TestCase):
    """Test class for backup_compliance."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.saved_path = f"{self.directory.path}/Compliance Policies/Policies/test_iosCompliancePolicy."
        self.expected_data = {
            "@odata.type": "#microsoft.graph.iosCompliancePolicy",
            "roleScopeTagIds": ["0"],
            "description": "Description value",
            "displayName": "test",
            "scheduledActionsForRule": [
                {
                    "ruleName": None,
                    "scheduledActionConfigurations": [{"gracePeriodHours": 0}],
                }
            ],
            "assignments": [{"target": {"groupName": "Group1"}}],
        }
        self.compliance_policy = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.iosCompliancePolicy",
                    "roleScopeTagIds": ["0"],
                    "id": "0",
                    "description": "Description value",
                    "displayName": "test",
                    "scheduledActionsForRule": [
                        {
                            "ruleName": None,
                            "scheduledActionConfigurations": [
                                {"id": "0", "gracePeriodHours": 0}
                            ],
                        }
                    ],
                }
            ]
        }

        self.batch_assignment_patch = patch(
            "src.IntuneCD.backup_compliance.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup_compliance.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup_compliance.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.compliance_policy

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        output = "yaml"
        count = savebackup(self.directory.path, output, self.exclude, self.token)

        with open(self.saved_path + output, "r") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        """The folder should be created, the file should have the expected contents, and the count should be 1."""
        self.assertTrue(
            Path(f"{self.directory.path}/Compliance Policies/Policies").exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        output = "json"
        count = savebackup(self.directory.path, output, self.exclude, self.token)

        with open(self.saved_path + output, "r") as f:
            saved_data = json.load(f)

        """The folder should be created, the file should have the expected contents, and the count should be 1."""
        self.assertTrue(
            Path(f"{self.directory.path}/Compliance Policies/Policies").exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, count["config_count"])

    def test_backup_with_no_returned_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = {"value": []}
        self.count = savebackup(self.directory.path, "json", self.exclude, self.token)
        self.assertEqual(0, self.count["config_count"])


if __name__ == "__main__":
    unittest.main()
