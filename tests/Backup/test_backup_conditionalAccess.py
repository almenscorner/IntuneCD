#!/usr/bin/env python3

"""This module tests backing up Conditional Access."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from testfixtures import TempDirectory
from src.IntuneCD.backup_conditionalAccess import savebackup

CA_POLICY = {
    "value": [{
        "id": 1,
        "displayName": "test",
        "conditions": {
                "clientAppTypes": ['all'],
                "applications": {
                    "includeApplications": ['All'],
                    "excludedApplications": ['d4ebce55-015a-49b5-a083-c84d1797ae8c']
                }},
        "grantControls": {
            "authenticationStrength@odata.context": 'context'}
    }]}

@patch("src.IntuneCD.backup_conditionalAccess.savebackup")
class TestBackupConditionalAccess(unittest.TestCase):
    """Test class for backup_conditionalAccess."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = 'token'
        self.saved_path = f"{self.directory.path}/Conditional Access/test."
        self.policy = {
                "value": [{
                    "id": 1,
                    "displayName": "test",
                    "conditions": {
                            "clientAppTypes": ['all'],
                            "applications": {
                                "includeApplications": ['All'],
                                "excludedApplications": ['d4ebce55-015a-49b5-a083-c84d1797ae8c']
                            }},
                    "grantControls": {
                        "authenticationStrength@odata.context": 'context'}
                }]}
        self.expected_data = {
                    "displayName": "test",
                    "conditions": {
                            "clientAppTypes": ['all'],
                            "applications": {
                                "includeApplications": ['All'],
                                "excludedApplications": ['d4ebce55-015a-49b5-a083-c84d1797ae8c']}},
                    "grantControls": {}}

        self.makeapirequest_patch = patch(
            'src.IntuneCD.backup_conditionalAccess.makeapirequest')
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.side_effect = [self.policy, self.policy['value'][0]]

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest.stop()

    def test_backup_yml(self, mock_data):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, 'yaml', self.token)

        with open(self.saved_path + 'yaml', 'r') as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(
            Path(f'{self.directory.path}/Conditional Access').exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count)

    def test_backup_json(self, mock_data):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, 'json', self.token)

        with open(self.saved_path + 'json', 'r') as f:
            self.saved_data = json.load(f)

        self.assertTrue(
            Path(f'{self.directory.path}/Conditional Access').exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count)

    def test_backup_with_no_return_data(self, mock_data):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.side_effect = [{'value': []}]
        self.count = savebackup(self.directory.path, 'json', self.token)
        self.assertEqual(0, self.count)


if __name__ == '__main__':
    unittest.main()
