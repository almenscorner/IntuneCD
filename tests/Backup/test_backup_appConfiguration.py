#!/usr/bin/env python3

"""This module tests backing up App Configuration."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from testfixtures import TempDirectory
from src.IntuneCD.backup_appConfiguration import savebackup

BATCH_ASSIGNMENT = [
    {
        'value': [
            {
                'id': '0',
                'target': {
                    'groupName': 'Group1'}}]}]
OBJECT_ASSIGNMENT = [
    {
        'target': {
            'groupName': 'Group1'}}]


class TestBackupAppConfig(unittest.TestCase):
    """Test class for backup_appConfiguration."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = 'token'
        self.exclude = []
        self.saved_path = f"{self.directory.path}/App Configuration/test_iosMobileAppConfiguration."
        self.expected_data = {
            '@odata.type': '#microsoft.graph.iosMobileAppConfiguration',
            'assignments': [
                {
                    'target': {
                        'groupName': 'Group1'}}],
            'displayName': 'test',
            'settings': [
                    {
                        'appConfigKey': 'sharedDevice',
                        'appConfigKeyType': 'booleanType',
                        'appConfigKeyValue': 'true'}],
            'targetedMobileApps': {
                'appName': 'Microsoft Authenticator',
                'type': '#microsoft.graph.iosVppApp'}}
        self.app_config = {
            '@odata.context': 'https://graph.microsoft.com/beta/$metadata#deviceAppManagement/mobileAppConfigurations',
            'value': [
                {
                    '@odata.type': '#microsoft.graph.iosMobileAppConfiguration',
                    'id': '0',
                    'targetedMobileApps': ['0'],
                    'displayName': 'test',
                    'settings': [
                        {
                            'appConfigKey': 'sharedDevice',
                            'appConfigKeyType': 'booleanType',
                            'appConfigKeyValue': 'true'}]}]}
        self.app_data = {
            '@odata.type': '#microsoft.graph.iosVppApp',
            'id': '0',
            'displayName': 'Microsoft Authenticator',
            'largeIcon': {
                'value': '/'},
            'licensingType': {
                'supportsDeviceLicensing': True},
            'applicableDeviceType': {
                'iPhoneAndIPod': True},
            'revokeLicenseActionResults': []}

        self.batch_assignment_patch = patch(
            'src.IntuneCD.backup_appConfiguration.batch_assignment')
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            'src.IntuneCD.backup_appConfiguration.get_object_assignment')
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch(
            'src.IntuneCD.backup_appConfiguration.makeapirequest')
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.side_effect = self.app_config, self.app_data

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path,
            'yaml',
            self.exclude,
            self.token)

        with open(self.saved_path + 'yaml', 'r') as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(
            Path(f'{self.directory.path}/App Configuration').exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count)

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path,
            'json',
            self.exclude,
            self.token)

        with open(self.saved_path + 'json', 'r') as f:
            saved_data = json.load(f)

        self.assertTrue(
            Path(f'{self.directory.path}/App Configuration').exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count)

    def test_backup_with_no_returned_data(self):
        """The count should be 0 if no data is returned."""
        self.makeapirequest.side_effect = [{'value': []}]
        self.count = savebackup(
            self.directory.path,
            'json',
            self.exclude,
            self.token)

        self.assertEqual(0, self.count)


if __name__ == '__main__':
    unittest.main()
