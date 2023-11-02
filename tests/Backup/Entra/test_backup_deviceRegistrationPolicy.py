#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up deviceRegistrationPolicy."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.Entra.backup_deviceRegistrationPolicy import savebackup


class TestBackupDeviceRegistrationPolicy(unittest.TestCase):
    """Test class for backup_deviceRegistrationPolicy."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.append_id = False
        self.saved_path = f"{self.directory.path}/Entra/Device Registration Policy/device_registration_policy."
        self.expected_data = {
            "multiFactorAuthConfiguration": "1",
            "displayName": "Device Registration Policy",
            "description": "Tenant-wide policy that manages initial provisioning controls using quota restrictions, additional authentication and authorization checks",
            "userDeviceQuota": 50,
            "azureADRegistration": {
                "appliesTo": "1",
                "allowedUsers": [],
                "allowedGroups": [],
                "isAdminConfigurable": False,
            },
            "azureADJoin": {
                "appliesTo": "1",
                "allowedUsers": [],
                "allowedGroups": [],
                "isAdminConfigurable": True,
            },
            "localAdminPassword": {"isEnabled": False},
        }
        self.deviceRegistrationPolicy = self.expected_data

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup.Entra.backup_deviceRegistrationPolicy.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest_patch.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.makeapirequest.return_value = self.deviceRegistrationPolicy
        self.count = savebackup(self.directory.path, "yaml", self.token)

        with open(self.saved_path + "yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(
            Path(f"{self.directory.path}/Entra/Device Registration Policy").exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.makeapirequest.return_value = self.deviceRegistrationPolicy
        self.count = savebackup(self.directory.path, "json", self.token)

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertTrue(
            Path(f"{self.directory.path}/Entra/Device Registration Policy").exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_return_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = None
        self.count = savebackup(self.directory.path, "json", self.token)
        self.assertEqual(0, self.count["config_count"])


if __name__ == "__main__":
    unittest.main()
