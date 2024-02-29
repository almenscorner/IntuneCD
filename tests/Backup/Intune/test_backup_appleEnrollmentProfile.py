#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up Apple Enrollment Profile."""

import json
import os.path
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.Intune.backup_appleEnrollmentProfile import savebackup


class TestBackupAppleEnrollmentProfile(unittest.TestCase):
    """Test class for backup_appleEnrollmentProfile."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.append_id = False
        self.saved_path = f"{self.directory.path}/Enrollment Profiles/Apple/test."
        self.expected_data = {
            "@odata.type": "#microsoft.graph.depMacOSEnrollmentProfile",
            "displayName": "test",
            "description": "",
            "requiresUserAuthentication": True,
            "configurationEndpointUrl": "https://appleconfigurator2.manage.microsoft.com/MDMServiceConfig?id=0",
            "enableAuthenticationViaCompanyPortal": False,
            "requireCompanyPortalOnSetupAssistantEnrolledDevices": False,
        }
        self.token_response = {
            "@odata.context": "https://graph.microsoft.com/beta/$metadata#deviceManagement/depOnboardingSettings",
            "@odata.count": 0,
            "value": [
                {
                    "id": "0000000",
                    "appleIdentifier": "awesome@example.com",
                    "tokenType": "dep",
                    "tokenName": "Test",
                    "roleScopeTagIds": ["0"],
                }
            ],
        }
        self.batch_intune = [
            {
                "value": [
                    {
                        "@odata.type": "#microsoft.graph.depMacOSEnrollmentProfile",
                        "id": "0",
                        "displayName": "test",
                        "description": "",
                        "requiresUserAuthentication": True,
                        "configurationEndpointUrl": "https://appleconfigurator2.manage.microsoft.com/MDMServiceConfig?id=0",
                        "enableAuthenticationViaCompanyPortal": False,
                        "requireCompanyPortalOnSetupAssistantEnrolledDevices": False,
                        "isDefault": True,
                    }
                ]
            }
        ]
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
            "src.IntuneCD.backup.Intune.backup_appleEnrollmentProfile.makeapirequest"
        )
        self.makeapirequest = self.patch_makeapirequest.start()

        self.patch_batch_request = patch(
            "src.IntuneCD.backup.Intune.backup_appleEnrollmentProfile.batch_request"
        )
        self.batch_request = self.patch_batch_request.start()

        self.makeAuditRequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_appleEnrollmentProfile.makeAuditRequest"
        )
        self.makeAuditRequest = self.makeAuditRequest_patch.start()
        self.makeAuditRequest.return_value = self.audit_data

        self.process_audit_data_patch = patch(
            "src.IntuneCD.backup.Intune.backup_appleEnrollmentProfile.process_audit_data"
        )
        self.process_audit_data = self.process_audit_data_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.patch_batch_request.stop()
        self.patch_makeapirequest.stop()
        self.makeAuditRequest_patch.stop()
        self.process_audit_data_patch.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""
        self.makeapirequest.return_value = self.token_response
        self.batch_request.return_value = self.batch_intune
        self.count = savebackup(
            self.directory.path, "yaml", self.token, "", self.append_id, False
        )

        with open(self.saved_path + "yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(
            Path(f"{self.directory.path}/Enrollment Profiles/Apple").exists()
        )
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""
        self.makeapirequest.return_value = self.token_response
        self.batch_request.return_value = self.batch_intune
        self.count = savebackup(
            self.directory.path, "json", self.token, "", self.append_id, False
        )

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(
            Path(f"{self.directory.path}/Enrollment Profiles/Apple").exists()
        )
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_return_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = {"value": []}
        self.count = savebackup(
            self.directory.path, "json", self.token, "", self.append_id, False
        )

        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if no data is returned."""

        self.batch_intune[0]["value"][0]["displayName"] = "test - test1"
        self.batch_request.return_value = self.batch_intune
        self.count = savebackup(
            self.directory.path, "json", self.token, "test", self.append_id, False
        )

        self.assertEqual(1, self.count["config_count"])
        self.assertTrue(
            os.path.exists(
                f"{self.directory.path}/Enrollment Profiles/Apple/test - test1.json"
            )
        )

    def test_backup_with_prefix_no_match(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = self.token_response
        self.batch_request.return_value = self.batch_intune
        self.count = savebackup(
            self.directory.path, "json", self.token, "prefix", self.append_id, False
        )

        self.assertFalse(
            os.path.exists(f"{self.directory.path}/Enrollment Profiles/Apple/test.json")
        )

    def test_backup_append_id(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""
        self.makeapirequest.return_value = self.token_response
        self.batch_request.return_value = self.batch_intune

        self.count = savebackup(
            self.directory.path, "json", self.token, "", True, False
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Enrollment Profiles/Apple/test__0.json"
            ).exists()
        )

    def test_backup_audit(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""
        self.makeapirequest.return_value = self.token_response
        self.batch_request.return_value = self.batch_intune

        self.count = savebackup(self.directory.path, "json", self.token, "", True, True)

        self.assertTrue(
            Path(
                f"{self.directory.path}/Enrollment Profiles/Apple/test__0.json"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
