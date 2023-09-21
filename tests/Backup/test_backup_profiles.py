#!/usr/bin/env python3

"""This module tests backing up profiles."""


import unittest

from pathlib import Path
from unittest.mock import patch
from testfixtures import TempDirectory
from src.IntuneCD.backup_profiles import savebackup

BATCH_ASSIGNMENT = [{"value": [{"target": {"groupName": "Group1"}}]}]
OBJECT_ASSIGNMENT = [{"target": {"groupName": "Group1"}}]


class TestBackupProfiles(unittest.TestCase):
    """Test class for backup_profiles."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []

        self.batch_assignment_patch = patch(
            "src.IntuneCD.backup_profiles.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup_profiles.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch("src.IntuneCD.backup_profiles.makeapirequest")
        self.makeapirequest = self.makeapirequest_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()

    def test_backup_macOS_custom_profile(self):
        """The folders and files should be created and the count should be 2."""

        self.makeapirequest.return_value = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.macOSCustomConfiguration",
                    "id": "0",
                    "displayName": "test",
                    "payload": "SGkgdGhlcmUgcHJldHR5",
                    "payloadFileName": "test.mobileconfig",
                }
            ]
        }

        self.count = savebackup(
            self.directory.path, "json", self.token, self.exclude, ""
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/test_macOSCustomConfiguration.json"
            ).exists()
        )
        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/mobileconfig/test.mobileconfig"
            ).exists()
        )
        self.assertEqual(2, self.count["config_count"])

    def test_backup_ios_custom_profile(self):
        """The folders and files should be created and the count should be 2."""

        self.makeapirequest.return_value = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.iosCustomConfiguration",
                    "id": "0",
                    "displayName": "test",
                    "payload": "SGkgdGhlcmUgcHJldHR5",
                    "payloadFileName": "test.mobileconfig",
                }
            ]
        }

        self.count = savebackup(
            self.directory.path, "json", self.token, self.exclude, ""
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/test_iosCustomConfiguration.json"
            ).exists()
        )
        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/mobileconfig/test.mobileconfig"
            ).exists()
        )
        self.assertEqual(2, self.count["config_count"])

    def test_backup_windows_custom_profile_encrypted(self):
        """The file should be created and the count should be 1."""

        self.profile = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.windows10CustomConfiguration",
                    "id": "0",
                    "displayName": "test",
                    "omaSettings": [
                        {
                            "isEncrypted": True,
                            "@odata.type": "#microsoft.graph.windows10OmaSetting",
                            "secretReferenceValueId": "0",
                            "omaUri": "test uri",
                            "displayName": "test",
                            "description": "",
                            "value": [],
                        }
                    ],
                }
            ]
        }
        self.oma_values = {
            "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
            "value": "password",
        }

        self.makeapirequest.side_effect = self.profile, self.oma_values

        self.count = savebackup(
            self.directory.path, "json", self.token, self.exclude, ""
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/test_windows10CustomConfiguration.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_windows_custom_profile_not_encrypted(self):
        """The file should be created and the count should be 1."""

        self.profile = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.windows10CustomConfiguration",
                    "id": "0",
                    "displayName": "test",
                    "omaSettings": [
                        {
                            "isEncrypted": False,
                            "@odata.type": "#microsoft.graph.windows10OmaSetting",
                            "secretReferenceValueId": "0",
                            "omaUri": "test uri",
                            "displayName": "test",
                            "description": "",
                            "value": [],
                        }
                    ],
                }
            ]
        }
        self.oma_values = {
            "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
            "value": "password",
        }

        self.makeapirequest.side_effect = self.profile, self.oma_values

        self.count = savebackup(
            self.directory.path, "json", self.token, self.exclude, ""
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/test_windows10CustomConfiguration.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_non_custom_profile(self):
        """The file should be created and the count should be 1."""

        self.makeapirequest.return_value = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.macOSGeneralDeviceConfiguration",
                    "id": "0",
                    "displayName": "test",
                }
            ]
        }

        self.count = savebackup(
            self.directory.path, "json", self.token, self.exclude, ""
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Device Configurations/test_macOSGeneralDeviceConfiguration.json"
            ).exists()
        )
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if no data is returned."""

        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, "test1"
        )
        self.assertEqual(0, self.count["config_count"])


if __name__ == "__main__":
    unittest.main()
