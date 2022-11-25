#!/usr/bin/env python3

"""This module tests updating Conditional Access."""

import unittest

from testfixtures import TempDirectory
from unittest.mock import patch
from src.IntuneCD.update_conditionalAccess import update


class TestUpdateConditionalAccess(unittest.TestCase):
    """Test class for update_compliance."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Conditional Access")
        self.directory.write(
            "Conditional Access/test.json", '{"test": "test"}',
            encoding='utf-8')
        self.directory.write(
            "Conditional Access/test.txt", 'txt',
            encoding='utf-8')
        self.token = 'token'
        self.mem_data = {"value": [{
                    "displayName": "test",
                    "id": 1,
                    "conditions": {
                            "clientAppTypes": ['all'],
                            "applications": {
                                "includeApplications": ['All'],
                                "excludedApplications": ['d4ebce55-015a-49b5-a083-c84d1797ae8c']}},
                    "grantControls": {}}]}
        self.repo_data = {
                    "displayName": "test",
                    "conditions": {
                            "clientAppTypes": ['all'],
                            "applications": {
                                "includeApplications": ['All'],
                                "excludedApplications": ['d4ebce55-015a-49b5-a083-c84d1797ae8c', '2']}},
                    "grantControls": {}}

        self.makeapirequest_patch = patch(
            'src.IntuneCD.update_conditionalAccess.makeapirequest')
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.load_file_patch = patch(
            'src.IntuneCD.update_conditionalAccess.load_file')
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            'src.IntuneCD.update_conditionalAccess.makeapirequestPatch')
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            'src.IntuneCD.update_conditionalAccess.makeapirequestPost')
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest.stop()
        self.load_file.stop()
        self.makeapirequestPatch.stop()
        self.makeapirequestPost.stop()

    def test_update_with_diffs(self):
        """The count should be 1 and the makeapirequestPatch should be called."""

        self.count = update(self.directory.path, self.token)

        self.assertEqual(self.count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)


    def test_update_with_no_diffs(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.repo_data['conditions']['applications']['excludedApplications'] = ['d4ebce55-015a-49b5-a083-c84d1797ae8c']

        self.count = update(self.directory.path, self.token)

        self.assertEqual(self.count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)

    def test_update_config_not_found(self):
        """The count should be 0 and makeapirequestPost should be called."""

        self.mem_data["value"][0]["displayName"] = "test1"
        self.makeapirequest.return_value = self.mem_data

        self.count = update(self.directory.path, self.token)

        self.assertEqual(self.count, 0)
        self.assertEqual(self.makeapirequestPost.call_count, 1)

    def test_update_config_no_id(self):
        """The count should be 0 and makeapirequestPost should not be called."""

        self.mem_data["value"][0].pop('id')
        self.makeapirequest.return_value = self.mem_data

        self.count = update(self.directory.path, self.token)

        self.assertEqual(self.count, 0)
        self.assertEqual(self.makeapirequestPost.call_count, 0)

    def test_update_config_grantControls(self):
        """The count should be 0 and makeapirequestPost should not be called."""

        self.repo_data['conditions']['applications']['excludedApplications'] = ['d4ebce55-015a-49b5-a083-c84d1797ae8c']
        self.mem_data["value"][0]['grantControls'] = {'authenticationStrength@odata.context': 'test'}
        self.makeapirequest.return_value = self.mem_data

        self.count = update(self.directory.path, self.token)

        self.assertEqual(self.count, 0)
        self.assertEqual(self.makeapirequestPost.call_count, 0)


if __name__ == '__main__':
    unittest.main()
