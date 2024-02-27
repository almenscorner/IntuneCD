#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up Managed Google Play."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.Intune.backup_managedGPlay import savebackup


class TestBackupManagedGPlay(unittest.TestCase):
    """Test class for backup_managedGPlay."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.append_id = False
        self.saved_path = (
            f"{self.directory.path}/Managed Google Play/awesome@gmail.com."
        )
        self.expected_data = {
            "bindStatus": "boundAndValidated",
            "lastAppSyncDateTime": "2022-01-28T12:28:48.975089Z",
            "lastAppSyncStatus": "success",
            "ownerUserPrincipalName": "awesome@gmail.com",
        }
        self.managed_gplay = {
            "id": "0",
            "bindStatus": "boundAndValidated",
            "lastAppSyncDateTime": "2022-01-28T12:28:48.975089Z",
            "lastAppSyncStatus": "success",
            "ownerUserPrincipalName": "awesome@gmail.com",
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
            "src.IntuneCD.backup.Intune.backup_managedGPlay.makeapirequest",
            return_value=self.managed_gplay,
        )
        self.makeapirequest = self.patch_makeapirequest.start()

        self.makeAuditRequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_managedGPlay.makeAuditRequest"
        )
        self.makeAuditRequest = self.makeAuditRequest_patch.start()
        self.makeAuditRequest.return_value = self.audit_data

        self.process_audit_data_patch = patch(
            "src.IntuneCD.backup.Intune.backup_managedGPlay.process_audit_data"
        )
        self.process_audit_data = self.process_audit_data_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest.stop()
        self.makeAuditRequest_patch.stop()
        self.process_audit_data_patch.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "yaml", self.exclude, self.token, self.append_id, False
        )

        with open(self.saved_path + "yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(Path(f"{self.directory.path}/Managed Google Play").exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, self.append_id, False
        )

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertTrue(Path(f"{self.directory.path}/Managed Google Play").exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_return_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = None
        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, self.append_id, False
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_append_id(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, True, False
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Managed Google Play/awesome@gmail.com__0.json"
            ).exists()
        )

    def test_backup_exclude_lastAppSyncDateTime(self):
        """The lastAppSyncDateTime should be excluded from the saved data."""

        self.exclude.append("GPlaySyncTime")
        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, self.append_id, False
        )

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertNotIn("lastAppSyncDateTime", saved_data)

    def test_backup_audit(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", self.exclude, self.token, True, True
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Managed Google Play/awesome@gmail.com__0.json"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
