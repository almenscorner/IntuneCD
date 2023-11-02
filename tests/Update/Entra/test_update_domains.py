# -*- coding: utf-8 -*-
import os
import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Entra.update_domains import update


class TestUpdateDomains(unittest.TestCase):
    """Test class for update_domains."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Domains")
        self.directory.write(
            "Entra/Domains/test.onmicrosoft.com.json",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.directory.write(
            "Entra/Domains/test.onmicrosoft.com.txt",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.token = "token"
        self.entra_data = {
            "value": [
                {
                    "authenticationType": "Managed",
                    "availabilityStatus": None,
                    "id": "test.onmicrosoft.com",
                    "isAdminManaged": True,
                    "isDefault": True,
                    "isInitial": True,
                    "isRoot": True,
                    "isVerified": True,
                    "supportedServices": ["Email", "OfficeCommunicationsOnline"],
                    "passwordValidityPeriodInDays": 2147483647,
                    "passwordNotificationWindowInDays": 14,
                    "state": None,
                }
            ]
        }
        self.repo_data = {
            "authenticationType": "Managed",
            "availabilityStatus": None,
            "id": "test.onmicrosoft.com",
            "isAdminManaged": True,
            "isDefault": False,
            "isInitial": True,
            "isRoot": True,
            "isVerified": True,
            "supportedServices": ["Email", "OfficeCommunicationsOnline"],
            "passwordValidityPeriodInDays": 2147483647,
            "passwordNotificationWindowInDays": 14,
            "state": None,
        }

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Entra.update_domains.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.entra_data

        self.load_file_patch = patch(
            "src.IntuneCD.update.Entra.update_domains.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Entra.update_domains.makeapirequestPatch"
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

        self.entra_data["value"][0]["isDefault"] = False
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)

    def test_update_with_no_file(self):
        """The count should be 0 and makeapirequestPatch should not be called."""

        os.remove(self.directory.path + "/Entra/Domains/test.onmicrosoft.com.json")
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPatch.call_count, 0)


if __name__ == "__main__":
    unittest.main()
