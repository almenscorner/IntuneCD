#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up remote assistance partner."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.Intune.backup_deviceManagementSettings import savebackup

DEVICE_MANAGEMENT_SETTINGS = {
    "deviceComplianceCheckinThresholdDays": 30,
    "isScheduledActionEnabled": True,
    "secureByDefault": False,
    "enhancedJailBreak": False,
    "deviceInactivityBeforeRetirementInDay": 0,
    "derivedCredentialProvider": "notConfigured",
    "derivedCredentialUrl": None,
    "androidDeviceAdministratorEnrollmentEnabled": False,
    "ignoreDevicesForUnsupportedSettingsEnabled": False,
    "enableLogCollection": True,
    "enableAutopilotDiagnostics": True,
    "enableEnhancedTroubleshootingExperience": False,
    "enableDeviceGroupMembershipReport": False,
}


@patch("src.IntuneCD.backup.Intune.backup_deviceManagementSettings.savebackup")
@patch(
    "src.IntuneCD.backup.Intune.backup_deviceManagementSettings.makeapirequest",
    return_value=DEVICE_MANAGEMENT_SETTINGS,
)
class TestBackupDeviceManagementSettings(unittest.TestCase):
    """Test class for backup_deviceManagementSettings."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.saved_path = f"{self.directory.path}/Device Management Settings/settings."
        self.expected_data = {
            "deviceComplianceCheckinThresholdDays": 30,
            "isScheduledActionEnabled": True,
            "secureByDefault": False,
            "enhancedJailBreak": False,
            "deviceInactivityBeforeRetirementInDay": 0,
            "derivedCredentialProvider": "notConfigured",
            "derivedCredentialUrl": None,
            "androidDeviceAdministratorEnrollmentEnabled": False,
            "ignoreDevicesForUnsupportedSettingsEnabled": False,
            "enableLogCollection": True,
            "enableAutopilotDiagnostics": True,
            "enableEnhancedTroubleshootingExperience": False,
            "enableDeviceGroupMembershipReport": False,
        }

    def tearDown(self):
        self.directory.cleanup()

    def test_backup_yml(self, _, __):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "yaml", self.token)

        with open(self.saved_path + "yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(
            Path(f"{self.directory.path}/Device Management Settings").exists()
        )
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self, _, __):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "json", self.token)

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            self.saved_data = json.load(f)

        self.assertTrue(
            Path(f"{self.directory.path}/Device Management Settings").exists()
        )
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])


if __name__ == "__main__":
    unittest.main()
