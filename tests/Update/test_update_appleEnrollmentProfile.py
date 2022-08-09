#!/usr/bin/env python3

"""This module tests updating Apple Enrollment Profiles."""

import unittest

from testfixtures import TempDirectory
from unittest.mock import patch
from src.IntuneCD.update_appleEnrollmentProfile import update


class TestUpdateAppleEnrollmentProfile(unittest.TestCase):
    """Test class for update_appleEnrollmentProfile."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Enrollment Profiles/Apple")
        self.directory.write(
            "Enrollment Profiles/Apple/test.json", '{"test": "test"}',
            encoding='utf-8')
        self.directory.write(
            "Enrollment Profiles/Apple/test.txt", '{"test": "test"}',
            encoding='utf-8')
        self.token = 'token'
        self.mem_data = {"value": [{"@odata.type": "test",
                                    "id": "0",
                                    "displayName": "test",
                                    "testvalue": "test"}]}
        self.repo_data = {"@odata.type": "test",
                          "id": "0",
                          "displayName": "test",
                          "testvalue": "test1"}

        self.makeapirequest_patch = patch(
            'src.IntuneCD.update_appleEnrollmentProfile.makeapirequest')
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.load_file_patch = patch(
            'src.IntuneCD.update_appleEnrollmentProfile.load_file')
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            'src.IntuneCD.update_appleEnrollmentProfile.makeapirequestPatch')
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest_patch.stop()
        self.load_file_patch.stop()
        self.makeapirequestPatch_patch.stop()

    def test_update_with_diffs(self):
        """The count should be 1 and makeapirequestPatch should be called."""

        self.count = update(self.directory.path, self.token)

        self.assertEqual(self.count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)

    def test_update_with_multiple_diffs(self):
        """The count should be 1 and makeapirequestPatch should be called."""

        self.repo_data['testvalue2'] = 'test2'
        self.mem_data['value'][0]['testvalue'] = 'test'
        self.mem_data['value'][0]['testvalue2'] = 'test1'

        self.count = update(self.directory.path, self.token)

        self.assertEqual(self.count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)

    def test_update_with_no_diffs(self):
        """The count should be 0 and makeapirequestPatch should not be called."""

        self.mem_data['value'][0]['testvalue'] = 'test1'
        self.count = update(self.directory.path, self.token)

        self.assertEqual(self.count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)


if __name__ == '__main__':
    unittest.main()
