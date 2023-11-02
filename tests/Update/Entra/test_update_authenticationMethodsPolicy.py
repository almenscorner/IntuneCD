# -*- coding: utf-8 -*-
import os
import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Entra.update_authenticationMethodsPolicy import update


class TestUpdateAuthenticationMethodsPolicy(unittest.TestCase):
    """Test class for update_authenticationMethodsPolicy."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Authentication Methods")
        self.directory.write(
            "Entra/Authentication Methods/authentication_methods.json",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.directory.write(
            "Entra/Authentication Methods/authentication_methods.txt",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.token = "token"
        self.entra_data = {
            "displayName": "Authentication Methods Policy",
            "description": "The tenant-wide policy that controls which authentication methods are allowed in the tenant, authentication method registration requirements, and self-service password reset settings",
            "policyVersion": "1.4",
            "policyMigrationState": "preMigration",
            "registrationEnforcement": {
                "authenticationMethodsRegistrationCampaign": {
                    "snoozeDurationInDays": 2,
                    "enforceRegistrationAfterAllowedSnoozes": True,
                    "state": "default",
                    "excludeTargets": [],
                    "includeTargets": [
                        {
                            "id": "all_users",
                            "targetType": "group",
                            "targetedAuthenticationMethod": "microsoftAuthenticator",
                        }
                    ],
                }
            },
            "authenticationMethodConfigurations@odata.context": "https://graph.microsoft.com/beta/$metadata#policies/authenticationMethodsPolicy/authenticationMethodConfigurations",
            "authenticationMethodConfigurations": [],
        }
        self.repo_data = {
            "displayName": "Authentication Methods Policy",
            "description": "The tenant-wide policy that controls which authentication methods are allowed in the tenant, authentication method registration requirements, and self-service password reset settings",
            "policyVersion": "1.4",
            "policyMigrationState": "preMigration",
            "registrationEnforcement": {
                "authenticationMethodsRegistrationCampaign": {
                    "snoozeDurationInDays": 1,
                    "enforceRegistrationAfterAllowedSnoozes": True,
                    "state": "default",
                    "excludeTargets": [],
                    "includeTargets": [
                        {
                            "id": "all_users",
                            "targetType": "group",
                            "targetedAuthenticationMethod": "microsoftAuthenticator",
                        }
                    ],
                }
            },
            "authenticationMethodConfigurations@odata.context": "https://graph.microsoft.com/beta/$metadata#policies/authenticationMethodsPolicy/authenticationMethodConfigurations",
            "authenticationMethodConfigurations": [],
        }

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Entra.update_authenticationMethodsPolicy.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.entra_data

        self.load_file_patch = patch(
            "src.IntuneCD.update.Entra.update_authenticationMethodsPolicy.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Entra.update_authenticationMethodsPolicy.makeapirequestPatch"
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

        self.entra_data["registrationEnforcement"][
            "authenticationMethodsRegistrationCampaign"
        ]["snoozeDurationInDays"] = 1
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)

    def test_update_with_no_file(self):
        """The count should be 0 and makeapirequestPatch should not be called."""

        os.remove(
            self.directory.path
            + "/Entra/Authentication Methods/authentication_methods.json"
        )
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPatch.call_count, 0)


if __name__ == "__main__":
    unittest.main()
