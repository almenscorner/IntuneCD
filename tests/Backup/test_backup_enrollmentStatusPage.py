#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up Enrollment Status Page profiles."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup_enrollmentStatusPage import savebackup

BATCH_ASSIGNMENT = [{"value": [{"id": "0", "target": {"groupName": "Group1"}}]}]
OBJECT_ASSIGNMENT = [{"target": {"groupName": "Group1"}}]


class TestBackupEnrollmentStatusPage(unittest.TestCase):
    """Test class for backup_enrollmentStatusPage."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.append_id = False
        self.saved_path = f"{self.directory.path}/Enrollment Profiles/Windows/ESP/test."
        self.expected_data = {
            "assignments": [{"target": {"groupName": "Group1"}}],
            "displayName": "test",
            "selectedMobileAppNames": [
                {"name": "app1", "type": "#microsoft.graph.mobileApp"}
            ],
            "@odata.type": "#microsoft.graph.windows10EnrollmentCompletionPageConfiguration",
        }
        self.statuspage_profile = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.windows10EnrollmentCompletionPageConfiguration",
                    "displayName": "test",
                    "id": "0",
                    "selectedMobileAppIds": ["0"],
                }
            ]
        }
        self.app_data = {
            "displayName": "app1",
            "@odata.type": "#microsoft.graph.mobileApp",
        }

        self.batch_assignment_patch = patch(
            "src.IntuneCD.backup_enrollmentStatusPage.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup_enrollmentStatusPage.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup_enrollmentStatusPage.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.side_effect = self.statuspage_profile, self.app_data

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        output = "yaml"
        count = savebackup(
            self.directory.path, output, self.exclude, self.token, "", self.append_id
        )

        with open(self.saved_path + output, "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(f"{self.directory.path}/Enrollment Profiles/Windows")
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        output = "json"
        count = savebackup(
            self.directory.path, output, self.exclude, self.token, "", self.append_id
        )

        with open(self.saved_path + output, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertTrue(f"{self.directory.path}/Enrollment Profiles/Windows/ESP")
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, count["config_count"])

    def test_backup_with_no_returned_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.side_effect = [{"value": []}]
        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, "", self.append_id
        )

        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if no data is returned."""

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
                f"{self.directory.path}/Enrollment Profiles/Windows/ESP/test__0.json"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
