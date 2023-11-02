# -*- coding: utf-8 -*-
import os
import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Entra.update_securityDefaults import update


class TestUpdateSecurityDefaults(unittest.TestCase):
    """Test class for update_securityDefaults."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Security Defaults")
        self.directory.write(
            "Entra/Security Defaults/security_defaults.json",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.token = "token"
        self.entra_data = {
            "displayName": "Security Defaults",
            "description": "Security defaults is a set of basic identity security mechanisms recommended by Microsoft. When enabled, these recommendations will be automatically enforced in your organization. Administrators and users will be better protected from common identity related attacks.",
            "isEnabled": False,
            "controlTypes": [],
            "securityDefaultsUpsell": {
                "action": "none",
                "dueDateTime": "2023-10-30T16:14:05.0071203Z",
            },
        }
        self.repo_data = {
            "displayName": "Security Defaults",
            "description": "Security defaults is a set of basic identity security mechanisms recommended by Microsoft. When enabled, these recommendations will be automatically enforced in your organization. Administrators and users will be better protected from common identity related attacks.",
            "isEnabled": True,
            "controlTypes": [],
            "securityDefaultsUpsell": {
                "action": "none",
                "dueDateTime": "2023-10-30T16:14:05.0071203Z",
            },
        }

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Entra.update_securityDefaults.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.entra_data

        self.load_file_patch = patch(
            "src.IntuneCD.update.Entra.update_securityDefaults.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Entra.update_securityDefaults.makeapirequestPatch"
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

        self.entra_data["isEnabled"] = True
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)

    def test_update_with_no_file(self):
        """The count should be 0 and makeapirequestPatch should not be called."""

        os.remove(
            self.directory.path + "/Entra/Security Defaults/security_defaults.json"
        )
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPatch.call_count, 0)


if __name__ == "__main__":
    unittest.main()
