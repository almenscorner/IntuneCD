# -*- coding: utf-8 -*-
import os
import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Entra.update_authorizationPolicy import update


class TestUpdateAuthorizationPolicy(unittest.TestCase):
    """Test class for update_authorizationPolicy."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Authorization Policy")
        self.directory.write(
            "Entra/Authorization Policy/authorization_policy.json",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.directory.write(
            "Entra/Authorization Policy/authorization_policy.txt",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.token = "token"
        self.entra_data = {
            "value": [
                {
                    "id": "authorizationPolicy",
                    "allowInvitesFrom": "none",
                    "allowedToSignUpEmailBasedSubscriptions": True,
                    "allowedToUseSSPR": False,
                    "allowEmailVerifiedUsersToJoinOrganization": False,
                    "allowUserConsentForRiskyApps": False,
                    "blockMsolPowerShell": False,
                    "description": "Used to manage authorization related settings across the company.",
                    "displayName": "Authorization Policy",
                    "enabledPreviewFeatures": [],
                    "guestUserRoleId": "10dae51f-b6af-4016-8d66-8c2a99b929b3",
                    "permissionGrantPolicyIdsAssignedToDefaultUserRole": [
                        "ManagePermissionGrantsForSelf.microsoft-user-default-legacy"
                    ],
                    "defaultUserRolePermissions": {
                        "allowedToCreateApps": True,
                        "allowedToCreateSecurityGroups": True,
                        "allowedToCreateTenants": True,
                        "allowedToReadBitlockerKeysForOwnedDevice": True,
                        "allowedToReadOtherUsers": True,
                    },
                }
            ]
        }
        self.repo_data = {
            "id": "authorizationPolicy",
            "allowInvitesFrom": "none",
            "allowedToSignUpEmailBasedSubscriptions": True,
            "allowedToUseSSPR": True,
            "allowEmailVerifiedUsersToJoinOrganization": False,
            "allowUserConsentForRiskyApps": False,
            "blockMsolPowerShell": False,
            "description": "Used to manage authorization related settings across the company.",
            "displayName": "Authorization Policy",
            "enabledPreviewFeatures": [],
            "guestUserRoleId": "10dae51f-b6af-4016-8d66-8c2a99b929b3",
            "permissionGrantPolicyIdsAssignedToDefaultUserRole": [
                "ManagePermissionGrantsForSelf.microsoft-user-default-legacy"
            ],
            "defaultUserRolePermissions": {
                "allowedToCreateApps": True,
                "allowedToCreateSecurityGroups": True,
                "allowedToCreateTenants": True,
                "allowedToReadBitlockerKeysForOwnedDevice": True,
                "allowedToReadOtherUsers": True,
            },
        }

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Entra.update_authorizationPolicy.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.entra_data

        self.load_file_patch = patch(
            "src.IntuneCD.update.Entra.update_authorizationPolicy.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Entra.update_authorizationPolicy.makeapirequestPatch"
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

        self.entra_data["value"][0]["allowedToUseSSPR"] = True
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)

    def test_update_with_no_file(self):
        """The count should be 0 and makeapirequestPatch should not be called."""

        os.remove(
            self.directory.path
            + "/Entra/Authorization Policy/authorization_policy.json"
        )
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPatch.call_count, 0)


if __name__ == "__main__":
    unittest.main()
