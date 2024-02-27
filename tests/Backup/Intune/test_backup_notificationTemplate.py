#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up Notification Templates."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.Intune.backup_notificationTemplate import savebackup


class TestBackupNotificationTemplate(unittest.TestCase):
    """Test class for backup_notificationTemplate."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.append_id = False
        self.saved_path = (
            f"{self.directory.path}/Compliance Policies/Message Templates/test."
        )
        self.expected_data = {
            "brandingOptions": "includeCompanyLogo,includeCompanyName,includeContactInformation",
            "defaultLocale": "da-dk",
            "displayName": "test",
            "localizedNotificationMessages": [
                {
                    "locale": "da-dk",
                    "messageTemplate": "Danish locale demo new",
                    "subject": "test",
                }
            ],
            "roleScopeTagIds": ["0"],
        }
        self.message_template = {
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

        self.localized_messages = {
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
        self.audit_data = {
            "value": [
                {
                    "resources": [
                        {"resourceId": "0", "auditResourceType": "MagicResource"}
                    ],
                    "activityDateTime": "2021-01-01T00:00:00Z",
                    "activityOperationType": "Patch",
                    "activityResult": "Success",
                    "actor": [{"auditActorType": "ItPro"}],
                }
            ]
        }

        self.patch_makeapirequest = patch(
            "src.IntuneCD.backup.Intune.backup_notificationTemplate.makeapirequest",
            side_effect=[self.message_template, self.localized_messages],
        )
        self.makeapirequest = self.patch_makeapirequest.start()

        self.makeAuditRequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_notificationTemplate.makeAuditRequest"
        )
        self.makeAuditRequest = self.makeAuditRequest_patch.start()
        self.makeAuditRequest.return_value = self.audit_data

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest.stop()
        self.makeAuditRequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "yaml", self.token, "", self.append_id, False, ""
        )

        with open(self.saved_path + "yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(
            Path(
                f"{self.directory.path}/Compliance Policies/Message Templates"
            ).exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", self.token, "", self.append_id, False, ""
        )

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertTrue(
            Path(
                f"{self.directory.path}/Compliance Policies/Message Templates"
            ).exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_return_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.side_effect = [{"value": []}]
        self.count = savebackup(
            self.directory.path, "json", self.token, "", self.append_id, False, ""
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if no data is returned."""

        self.count = savebackup(
            self.directory.path, "json", self.token, "test1", self.append_id, False, ""
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_append_id(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", self.token, "", True, False, ""
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Compliance Policies/Message Templates/test__0.json"
            ).exists()
        )

    def test_backup_scope_tags_and_audit(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            "",
            True,
            True,
            [{"id": 0, "displayName": "default"}],
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Compliance Policies/Message Templates/test__0.json"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
