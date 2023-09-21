#!/usr/bin/env python3

"""This module tests backing up Notification Templates."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from testfixtures import TempDirectory
from src.IntuneCD.backup_notificationTemplate import savebackup


def side_effects_makeapirequest():
    """Mock function for makeapirequest."""

    MESSAGE_TEMPLATE = {
        "value": [
            {
                "id": "0",
                "displayName": "test",
                "defaultLocale": "da-dk",
                "brandingOptions": "includeCompanyLogo,includeCompanyName,includeContactInformation",
                "roleScopeTagIds": ["0"],
                "localizedNotificationMessages": [
                    {
                        "id": "0",
                        "lastModifiedDateTime": "2022-07-16T00:01:14.8680508Z",
                        "locale": "da-dk",
                        "subject": "test",
                        "messageTemplate": "Danish locale demo new",
                        "isDefault": True,
                    }
                ],
            }
        ]
    }

    LOCALIZED_MESSAGES = {
        "id": "0",
        "displayName": "test",
        "defaultLocale": "da-dk",
        "brandingOptions": "includeCompanyLogo,includeCompanyName,includeContactInformation",
        "roleScopeTagIds": ["0"],
        "localizedNotificationMessages": [
            {
                "id": "0",
                "lastModifiedDateTime": "2022-07-16T00:03:39.8347438Z",
                "locale": "da-dk",
                "subject": "test",
                "messageTemplate": "Danish locale demo new",
                "isDefault": True,
            }
        ],
    }

    return MESSAGE_TEMPLATE, LOCALIZED_MESSAGES


@patch("src.IntuneCD.backup_notificationTemplate.savebackup")
@patch(
    "src.IntuneCD.backup_notificationTemplate.makeapirequest",
    side_effect=side_effects_makeapirequest(),
)
class TestBackupNotificationTemplate(unittest.TestCase):
    """Test class for backup_notificationTemplate."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.saved_path = (
            f"{self.directory.path}/Compliance Policies/Message Templates/test."
        )
        self.expected_data = {
            "brandingOptions": "includeCompanyLogo,includeCompanyName,includeContactInformation",
            "defaultLocale": "da-dk",
            "displayName": "test",
            "localizedNotificationMessages": [
                {
                    "isDefault": True,
                    "locale": "da-dk",
                    "messageTemplate": "Danish locale demo new",
                    "subject": "test",
                }
            ],
            "roleScopeTagIds": ["0"],
        }

    def tearDown(self):
        self.directory.cleanup()

    def test_backup_yml(self, mock_data, mock_makeapirequest):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "yaml", self.token, "")

        with open(self.saved_path + "yaml", "r") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(
            Path(
                f"{self.directory.path}/Compliance Policies/Message Templates"
            ).exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self, mock_data, mock_makeapirequest):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "json", self.token, "")

        with open(self.saved_path + "json", "r") as f:
            saved_data = json.load(f)

        self.assertTrue(
            Path(
                f"{self.directory.path}/Compliance Policies/Message Templates"
            ).exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_return_data(self, mock_data, mock_makeapirequest):
        """The count should be 0 if no data is returned."""

        mock_data.side_effect = [{"value": []}]
        self.count = savebackup(self.directory.path, "json", self.token, "")
        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_prefix(self, mock_data, mock_makeapirequest):
        """The count should be 0 if no data is returned."""

        self.count = savebackup(self.directory.path, "json", self.token, "test1")
        self.assertEqual(0, self.count["config_count"])


if __name__ == "__main__":
    unittest.main()
