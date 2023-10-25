# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.update_deviceManagementSettings import update


class TestUpdateDeviceManagementSettings(unittest.TestCase):
    """Test class for update_deviceManagementSettings."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Device Management Settings")
        self.directory.write(
            "Device Management Settings/test.json", '{"test": "test"}', encoding="utf-8"
        )
        self.directory.write(
            "Device Management Settings/test.txt", '{"test": "test"}', encoding="utf-8"
        )
        self.token = "token"
        self.mem_data = {
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
        self.repo_data = {
            "deviceComplianceCheckinThresholdDays": 30,
            "isScheduledActionEnabled": True,
            "secureByDefault": True,
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

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.update_deviceManagementSettings.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.load_file_patch = patch(
            "src.IntuneCD.update.update_deviceManagementSettings.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.update_deviceManagementSettings.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update.update_deviceManagementSettings.makeapirequestPost"
        )

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest_patch.stop()
        self.load_file_patch.stop()
        self.makeapirequestPatch_patch.stop()

    def test_update_with_diffs(self):
        """The count should be 1 and makeapirequestPatch should be called."""

        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)

    def test_update_with_multiple_diffs(self):
        """The count should be 1 and makeapirequestPatch should be called."""

        self.repo_data["enhancedJailBreak"] = True

        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)

    def test_update_with_no_diffs(self):
        """The count should be 0 and makeapirequestPatch should not be called."""

        self.mem_data["secureByDefault"] = True
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)


if __name__ == "__main__":
    unittest.main()
