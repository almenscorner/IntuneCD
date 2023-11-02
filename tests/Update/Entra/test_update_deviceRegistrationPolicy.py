# -*- coding: utf-8 -*-
import os
import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Entra.update_deviceRegistrationPolicy import update


class TestUpdateDeviceRegistrationPolicy(unittest.TestCase):
    """Test class for update_deviceRegistrationPolicy."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Device Registration Policy")
        self.directory.write(
            "Entra/Device Registration Policy/device_registration_policy.json",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.directory.write(
            "Entra/Device Registration Policy/device_registration_policy.txt",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.token = "token"
        self.entra_data = {
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
        self.repo_data = {
            "multiFactorAuthConfiguration": "1",
            "displayName": "Device Registration Policy",
            "description": "Tenant-wide policy that manages initial provisioning controls using quota restrictions, additional authentication and authorization checks",
            "userDeviceQuota": 49,
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

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Entra.update_deviceRegistrationPolicy.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.entra_data

        self.load_file_patch = patch(
            "src.IntuneCD.update.Entra.update_deviceRegistrationPolicy.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Entra.update_deviceRegistrationPolicy.makeapirequestPut"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

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

    def test_update_with_no_diffs(self):
        """The count should be 0 and makeapirequestPatch should not be called."""

        self.entra_data["userDeviceQuota"] = 49
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)

    def test_update_with_no_file(self):
        """The count should be 0 and makeapirequestPatch should not be called."""

        os.remove(
            self.directory.path
            + "/Entra/Device Registration Policy/device_registration_policy.json"
        )
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPatch.call_count, 0)


if __name__ == "__main__":
    unittest.main()
