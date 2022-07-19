#!/usr/bin/env python3

"""This module tests backing up Apple Enrollment Profile."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from src.IntuneCD.backup_appleEnrollmentProfile import savebackup
from testfixtures import TempDirectory

TOKEN_RESPONSE = {
    '@odata.context': 'https://graph.microsoft.com/beta/$metadata#deviceManagement/depOnboardingSettings',
    '@odata.count': 0,
    'value': [
        {
            'id': '0000000',
            'appleIdentifier': 'awesome@example.com',
            'tokenType': 'dep',
            'tokenName': 'Test',
            'roleScopeTagIds': ['0']}]}
BATCH_INTUNE = [
    {
        'value': [
            {
                '@odata.type': '#microsoft.graph.depMacOSEnrollmentProfile',
                'id': '0',
                'displayName': 'test',
                'description': '',
                'requiresUserAuthentication': True,
                'configurationEndpointUrl': 'https://appleconfigurator2.manage.microsoft.com/MDMServiceConfig?id=0',
                'enableAuthenticationViaCompanyPortal': False,
                'requireCompanyPortalOnSetupAssistantEnrolledDevices': False,
                'isDefault': True}]}]


@patch("src.IntuneCD.backup_appleEnrollmentProfile.savebackup")
@patch("src.IntuneCD.backup_appleEnrollmentProfile.makeapirequest",
       return_value=TOKEN_RESPONSE)
@patch("src.IntuneCD.backup_appleEnrollmentProfile.batch_request",
       return_value=BATCH_INTUNE)
class TestBackupAppleEnrollmentProfile(unittest.TestCase):
    """Test class for backup_appleEnrollmentProfile."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = 'token'
        self.saved_path = f"{self.directory.path}/Enrollment Profiles/Apple/test."
        self.expected_data = {
            '@odata.type': '#microsoft.graph.depMacOSEnrollmentProfile',
            'displayName': 'test',
            'description': '',
            'requiresUserAuthentication': True,
            'configurationEndpointUrl': 'https://appleconfigurator2.manage.microsoft.com/MDMServiceConfig?id=0',
            'enableAuthenticationViaCompanyPortal': False,
            'requireCompanyPortalOnSetupAssistantEnrolledDevices': False,
            'isDefault': True}

    def tearDown(self):
        self.directory.cleanup()

    def test_backup_yml(
            self,
            mock_data,
            mock_makeapirequest,
            mock_batch_request):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, 'yaml', self.token)

        with open(self.saved_path + 'yaml', 'r') as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(Path(f'{self.directory.path}/Enrollment Profiles/Apple').exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count)

    def test_backup_json(
            self,
            mock_data,
            mock_makeapirequest,
            mock_batch_request):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, 'json', self.token)

        with open(self.saved_path + 'json', 'r') as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(Path(f'{self.directory.path}/Enrollment Profiles/Apple').exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count)

    def test_backup_with_no_return_data(
            self,
            mock_data,
            mock_makeapirequest,
            mock_batch_request):
        """The count should be 0 if no data is returned."""

        mock_makeapirequest.return_value = {'value': []}
        self.count = savebackup(self.directory.path, 'json', self.token)

        self.assertEqual(0, self.count)


if __name__ == '__main__':
    unittest.main()
