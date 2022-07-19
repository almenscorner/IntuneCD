#!/usr/bin/env python3

"""This module tests backing up Managed Google Play."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from src.IntuneCD.backup_managedGPlay import savebackup
from testfixtures import TempDirectory

MANAGED_GPLAY = {
            "id": "0",
          "bindStatus": "boundAndValidated",
          "lastAppSyncDateTime": "2022-01-28T12:28:48.975089Z",
          "lastAppSyncStatus": "success",
          "ownerUserPrincipalName": "awesome@gmail.com",
}


@patch("src.IntuneCD.backup_managedGPlay.savebackup")
@patch("src.IntuneCD.backup_managedGPlay.makeapirequest", return_value=MANAGED_GPLAY)
class TestBackupManagedGPlay(unittest.TestCase):
    """Test class for backup_managedGPlay."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = 'token'
        self.saved_path = f"{self.directory.path}/Managed Google Play/awesome@gmail.com."
        self.expected_data = {
          "bindStatus": "boundAndValidated",
          "lastAppSyncDateTime": "2022-01-28T12:28:48.975089Z",
          "lastAppSyncStatus": "success",
          "ownerUserPrincipalName": "awesome@gmail.com",
}

    def tearDown(self):
        self.directory.cleanup()


    def test_backup_yml(self, mock_data, mock_makeapirequest):
        self.count = savebackup(self.directory.path, 'yaml', self.token)

        with open(self.saved_path + 'yaml', 'r') as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(Path(f'{self.directory.path}/Managed Google Play').exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count)

    def test_backup_json(self, mock_data, mock_makeapirequest):
        self.count = savebackup(self.directory.path, 'json', self.token)

        with open(self.saved_path + 'json', 'r') as f:
            saved_data = json.load(f)

        self.assertTrue(Path(f'{self.directory.path}/Managed Google Play').exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count)

    def test_backup_with_no_return_data(self, mock_data, mock_makeapirequest):
        mock_data.return_value = None
        self.count = savebackup(self.directory.path, 'json', self.token)
        self.assertEqual(0, self.count)
