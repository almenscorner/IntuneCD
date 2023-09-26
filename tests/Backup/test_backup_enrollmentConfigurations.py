#!/usr/bin/env python3

import json
import yaml
import unittest

from unittest.mock import patch
from testfixtures import TempDirectory
from src.IntuneCD.backup_enrollmentConfigurations import savebackup

BATCH_ASSIGNMENT = [{"value": [{"id": "0", "target": {"groupName": "Group1"}}]}]
OBJECT_ASSIGNMENT = [{"target": {"groupName": "Group1"}}]


class TestBackupEnrollmentConfigurations(unittest.TestCase):
    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.saved_path = f"{self.directory.path}/Enrollment Configurations/test_test."
        self.expected_data = {
            "@odata.type": "test.test.test",
            "assignments": [{"target": {"groupName": "Group1"}}],
            "displayName": "test",
            "deviceEnrollmentConfigurationType": "singlePlatformRestriction",
            "platformType": "android",
            "platformRestriction": {
                "platformBlocked": False,
                "personalDeviceEnrollmentBlocked": False,
            },
        }
        self.enrollment_config = {
            "value": [
                {
                    "@odata.type": "test.test.test",
                    "id": "test",
                    "displayName": "test",
                    "deviceEnrollmentConfigurationType": "singlePlatformRestriction",
                    "platformType": "android",
                    "platformRestriction": {
                        "platformBlocked": False,
                        "personalDeviceEnrollmentBlocked": False,
                    },
                }
            ]
        }

        self.batch_assignment_patch = patch(
            "src.IntuneCD.backup_enrollmentConfigurations.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup_enrollmentConfigurations.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup_enrollmentConfigurations.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.enrollment_config

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()

    def test_backup_yml(self):
        """Test that the backup is saved as yml. And that the data is correct."""
        output = "yaml"
        count = savebackup(self.directory.path, output, self.exclude, self.token, "")
        with open(f"{self.saved_path}yaml", "r") as file:
            data = yaml.safe_load(file)
        self.assertEqual(data, self.expected_data)

    def test_backup_json(self):
        """Test that the backup is saved as json. And that the data is correct."""
        output = "json"
        count = savebackup(self.directory.path, output, self.exclude, self.token, "")
        with open(f"{self.saved_path}json", "r") as file:
            data = yaml.safe_load(file)
        self.assertEqual(data, self.expected_data)

    def test_backup_skip_ESP(self):
        """Test that the backup is skipped when config is ESP."""
        output = "json"
        self.enrollment_config["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.windows10EnrollmentCompletionPageConfiguration"
        count = savebackup(self.directory.path, output, self.exclude, self.token, "")

        self.assertEqual(0, count["config_count"])

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
