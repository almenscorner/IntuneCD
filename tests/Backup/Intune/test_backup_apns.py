#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up APNS."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.Intune.backup_apns import savebackup


class TestBackupAPNS(unittest.TestCase):
    """Test class for backup_apns."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.append_id = False
        self.saved_path = (
            f"{self.directory.path}/Apple Push Notification/awesome@example.com."
        )
        self.expected_data = {
            "appleIdentifier": "awesome@example.com",
            "expirationDateTime": "2023-04-01T13:59:54Z",
            "certificateUploadStatus": None,
            "certificateUploadFailureReason": None,
            "certificateSerialNumber": "11000000000000",
        }
        self.apns = {
            "@odata.context": "https://graph.microsoft.com/beta/$metadata#deviceManagement/applePushNotificationCertificate/$entity",
            "id": "00000000-0000-0000-0000-000000000000",
            "appleIdentifier": "awesome@example.com",
            "topicIdentifier": "com.apple.mgmt.External.ef285859-4227-415c-8b08-826b610f2034",
            "lastModifiedDateTime": "2022-04-01T14:10:18Z",
            "expirationDateTime": "2023-04-01T13:59:54Z",
            "certificateUploadStatus": None,
            "certificateUploadFailureReason": None,
            "certificateSerialNumber": "11000000000000",
            "certificate": None,
        }

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_apns.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest_patch.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.makeapirequest.return_value = self.apns
        self.count = savebackup(self.directory.path, "yaml", False, self.token)

        with open(self.saved_path + "yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(Path(f"{self.directory.path}/Apple Push Notification").exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.makeapirequest.return_value = self.apns
        self.count = savebackup(self.directory.path, "json", False, self.token)

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertTrue(Path(f"{self.directory.path}/Apple Push Notification").exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_return_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = None
        self.count = savebackup(self.directory.path, "json", False, self.token)
        self.assertEqual(0, self.count["config_count"])


if __name__ == "__main__":
    unittest.main()
