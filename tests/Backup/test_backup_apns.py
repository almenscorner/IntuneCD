#!/usr/bin/env python3

"""This module tests backing up APNS."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from testfixtures import TempDirectory
from src.IntuneCD.backup_apns import savebackup

APNS = {
    "@odata.context": "https://graph.microsoft.com/beta/$metadata#deviceManagement/applePushNotificationCertificate/$entity",
    "id": "00000000-0000-0000-0000-000000000000",
    "appleIdentifier": "awesome@example.com",
    "topicIdentifier": "com.apple.mgmt.External.ef285859-4227-415c-8b08-826b610f2034",
    "lastModifiedDateTime": "2022-04-01T14:10:18Z",
    "expirationDateTime": "2023-04-01T13:59:54Z",
    "certificateUploadStatus": None,
    "certificateUploadFailureReason": None,
    "certificateSerialNumber": "11000000000000",
    "certificate": None}


@patch("src.IntuneCD.backup_apns.savebackup")
@patch("src.IntuneCD.backup_apns.makeapirequest", return_value=APNS)
class TestBackupAPNS(unittest.TestCase):
    """Test class for backup_apns."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = 'token'
        self.saved_path = f"{self.directory.path}/Apple Push Notification/awesome@example.com."
        self.expected_data = {
            "appleIdentifier": "awesome@example.com",
            "expirationDateTime": "2023-04-01T13:59:54Z",
            "certificateUploadStatus": None,
            "certificateUploadFailureReason": None,
            "certificateSerialNumber": "11000000000000"}

    def tearDown(self):
        self.directory.cleanup()

    def test_backup_yml(self, mock_data, mock_makeapirequest):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, 'yaml', self.token)

        with open(self.saved_path + 'yaml', 'r') as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(
            Path(f'{self.directory.path}/Apple Push Notification').exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count)

    def test_backup_json(self, mock_data, mock_makeapirequest):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, 'json', self.token)

        with open(self.saved_path + 'json', 'r') as f:
            saved_data = json.load(f)

        self.assertTrue(
            Path(f'{self.directory.path}/Apple Push Notification').exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count)

    def test_backup_with_no_return_data(self, mock_data, mock_makeapirequest):
        """The count should be 0 if no data is returned."""

        mock_data.return_value = None
        self.count = savebackup(self.directory.path, 'json', self.token)
        self.assertEqual(0, self.count)


if __name__ == '__main__':
    unittest.main()
