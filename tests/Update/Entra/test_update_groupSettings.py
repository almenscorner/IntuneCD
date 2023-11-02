# -*- coding: utf-8 -*-
import os
import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Entra.update_groupSettings import update


class TestUpdategroupSettings(unittest.TestCase):
    """Test class for update_groupSettings."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Group Settings")
        self.directory.write(
            "Entra/Group Settings/Group.Unified.json",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.token = "token"
        self.entra_data = {
            "value": [
                {
                    "id": "1",
                    "displayName": "Group.Unified",
                    "templateId": "62375ab9-6b52-47ed-826b-58e47e0e304b",
                    "values": [
                        {"name": "AllowGuestsToBeGroupOwner", "value": "false"},
                    ],
                }
            ]
        }
        self.repo_data = {
            "displayName": "Group.Unified",
            "templateId": "62375ab9-6b52-47ed-826b-58e47e0e304b",
            "values": [
                {"name": "AllowGuestsToBeGroupOwner", "value": "true"},
            ],
        }

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Entra.update_groupSettings.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.entra_data

        self.load_file_patch = patch(
            "src.IntuneCD.update.Entra.update_groupSettings.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Entra.update_groupSettings.makeapirequestPatch"
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

        self.entra_data["value"][0]["values"][0]["value"] = "true"
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)

    def test_update_with_no_file(self):
        """The count should be 0 and makeapirequestPatch should not be called."""

        os.remove(self.directory.path + "/Entra/Group Settings/Group.Unified.json")
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPatch.call_count, 0)


if __name__ == "__main__":
    unittest.main()
