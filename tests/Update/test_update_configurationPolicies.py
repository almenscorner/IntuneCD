#!/usr/bin/env python3

"""This module tests updating Configuration Policies."""

import unittest

from testfixtures import TempDirectory
from unittest.mock import patch
from src.IntuneCD.update_configurationPolicies import update


class TestUpdateConfigurationPolicies(unittest.TestCase):
    """Test class for update_configurationPolicies."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Settings Catalog")
        self.directory.write(
            "Settings Catalog/test.json", '{"test": "test"}',
            encoding='utf-8')
        self.token = 'token'
        self.mem_data = {"value": [{"@odata.type": "test",
                                    "id": "0",
                                    "name": "test",
                                    "testvalue": "test",
                                    "settings": [{"id": "0",
                                                  "testvalue": "test"}],
                                    "assignments": [{"target": {"groupId": "test"}}]}]}
        self.repo_data = {"@odata.type": "test",
                          "id": "0",
                          "name": "test",
                          "testvalue": "test1",
                          "settings": [
                              {
                                  "id": "0",
                                  "testvalue": "test1"}],
                          "assignments": [{"target": {"groupName": "test1"}}]}

        self.batch_assignment_patch = patch(
            'src.IntuneCD.update_configurationPolicies.batch_assignment')
        self.batch_assignment = self.batch_assignment_patch.start()

        self.object_assignment_patch = patch(
            'src.IntuneCD.update_configurationPolicies.get_object_assignment')
        self.object_assignment = self.object_assignment_patch.start()

        self.makeapirequest_patch = patch(
            'src.IntuneCD.update_configurationPolicies.makeapirequest')
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.update_assignment_patch = patch(
            'src.IntuneCD.update_configurationPolicies.update_assignment')
        self.update_assignment = self.update_assignment_patch.start()

        self.load_file_patch = patch(
            'src.IntuneCD.update_configurationPolicies.load_file')
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.post_assignment_update_patch = patch(
            'src.IntuneCD.update_configurationPolicies.post_assignment_update')
        self.post_assignment_update = self.post_assignment_update_patch.start()

        self.makeapirequestPatch_patch = patch(
            'src.IntuneCD.update_configurationPolicies.makeapirequestPut')
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            'src.IntuneCD.update_configurationPolicies.makeapirequestPost')
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()
        self.update_assignment.stop()
        self.load_file.stop()
        self.post_assignment_update.stop()
        self.makeapirequestPatch.stop()
        self.makeapirequestPost.stop()

    def test_update_with_diffs_and_assignment(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_diffs_no_assignment(self):
        """The count should be 1 and the makeapirequestPatch should be called."""

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_with_no_diffs_and_assignment(self):
        """The count should be 0, the post_assignment_update should be called,
         and makeapirequestPatch should not be called."""

        self.mem_data["value"][0]["testvalue"] = "test1"

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_no_diffs_no_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.mem_data["value"][0]["testvalue"] = "test1"

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_config_not_found_and_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.mem_data["value"][0]["name"] = "test1"

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count, 0)
        self.assertEqual(self.makeapirequestPost.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)


if __name__ == '__main__':
    unittest.main()
