# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update_assignmentFilter import update


class TestUpdateAssignmentFilter(unittest.TestCase):
    """Test class for update_assignmentFilter."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Filters")
        self.directory.write("Filters/test.json", '{"test": "test"}', encoding="utf-8")
        self.directory.write("Filters/test.txt", '{"test": "test"}', encoding="utf-8")
        self.token = "token"
        self.mem_data = {
            "value": [
                {
                    "@odata.type": "test",
                    "id": "0",
                    "displayName": "test",
                    "testvalue": "test",
                }
            ]
        }
        self.repo_data = {
            "@odata.type": "test",
            "id": "0",
            "displayName": "test",
            "testvalue": "test1",
        }

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update_assignmentFilter.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.load_file_patch = patch("src.IntuneCD.update_assignmentFilter.load_file")
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update_assignmentFilter.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update_assignmentFilter.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest_patch.stop()
        self.load_file_patch.stop()
        self.makeapirequestPatch_patch.stop()
        self.makeapirequestPost_patch.stop()

    def test_update_with_diffs(self):
        """The count should be 1 and makeapirequestPatch should be called."""

        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)

    def test_update_with_multiple_diffs(self):
        """The count should be 1 and makeapirequestPatch should be called."""

        self.repo_data["testvalue2"] = "test2"
        self.mem_data["value"][0]["testvalue"] = "test"
        self.mem_data["value"][0]["testvalue2"] = "test1"

        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)

    def test_update_with_no_diffs(self):
        """The count should be 0 and makeapirequestPatch should not be called."""

        self.mem_data["value"][0]["testvalue"] = "test1"
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)

    def test_update_config_not_found(self):
        """The count should be 0 and makeapirequestPost should be called."""

        self.mem_data["value"][0]["displayName"] = "test1"
        self.count = update(self.directory.path, self.token, report=False)

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)


if __name__ == "__main__":
    unittest.main()
