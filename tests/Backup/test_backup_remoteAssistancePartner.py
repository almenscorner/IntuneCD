#!/usr/bin/env python3

"""This module tests backing up remote assistance partner."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from testfixtures import TempDirectory
from src.IntuneCD.backup_remoteAssistancePartner import savebackup

REMOTE_ASSISTANCE_PARTNER = {
    "value": [{"id": "0", "onboardingStatus": "onboarded", "displayName": "test"}]
}


@patch("src.IntuneCD.backup_remoteAssistancePartner.savebackup")
@patch(
    "src.IntuneCD.backup_remoteAssistancePartner.makeapirequest",
    return_value=REMOTE_ASSISTANCE_PARTNER,
)
class TestBackupCompliancePartner(unittest.TestCase):
    """Test class for backup_remoteAssistancePartner."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.saved_path = (
            f"{self.directory.path}/Partner Connections/Remote Assistance/test."
        )
        self.expected_data = {"onboardingStatus": "onboarded", "displayName": "test"}

    def tearDown(self):
        self.directory.cleanup()

    def test_backup_yml(self, mock_data, mock_makeapirequest):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "yaml", self.token)

        with open(self.saved_path + "yaml", "r") as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(
            Path(
                f"{self.directory.path}/Partner Connections/Remote Assistance"
            ).exists()
        )
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self, mock_data, mock_makeapirequest):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "json", self.token)

        with open(self.saved_path + "json", "r") as f:
            self.saved_data = json.load(f)

        self.assertTrue(
            Path(
                f"{self.directory.path}/Partner Connections/Remote Assistance"
            ).exists()
        )
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_onboarding_status_not_onboarded(self, mock_data, mock_makeapirequest):
        """The count should be 0 if the onboarding status is not onboarded."""

        mock_data.return_value = {"value": [{"onboardingStatus": "notOnboarded"}]}
        self.count = savebackup(self.directory.path, "json", self.token)
        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_no_return_data(self, mock_data, mock_makeapirequest):
        """The count should be 0 if no data is returned."""

        mock_data.return_value = {"value": []}
        self.count = savebackup(self.directory.path, "json", self.token)
        self.assertEqual(0, self.count["config_count"])


if __name__ == "__main__":
    unittest.main()
