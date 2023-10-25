#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests updating Enrollment Configurations."""

import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.update_enrollmentConfigurations import update


class TestUpdateEnrollmentStatusPage(unittest.TestCase):
    """Test class for update_enrollmentConfigurations."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Enrollment Configurations")
        self.directory.write(
            "Enrollment Configurations/test_deviceEnrollmentPlatformRestrictionConfiguration.json",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.token = "token"
        self.mem_data = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.deviceEnrollmentPlatformRestrictionConfiguration",
                    "id": "test",
                    "priority": 1,
                    "displayName": "test",
                    "deviceEnrollmentConfigurationType": "singlePlatformRestriction",
                    "platformType": "android",
                    "platformRestriction": {
                        "platformBlocked": True,
                        "personalDeviceEnrollmentBlocked": False,
                    },
                }
            ]
        }
        self.repo_data = {
            "@odata.type": "#microsoft.graph.deviceEnrollmentPlatformRestrictionConfiguration",
            "assignments": [{"target": {"groupName": "Group1"}}],
            "displayName": "test",
            "priority": 1,
            "deviceEnrollmentConfigurationType": "singlePlatformRestriction",
            "platformType": "android",
            "platformRestriction": {
                "platformBlocked": False,
                "personalDeviceEnrollmentBlocked": False,
            },
        }

        self.batch_assignment_patch = patch(
            "src.IntuneCD.update.update_enrollmentConfigurations.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()

        self.object_assignment_patch = patch(
            "src.IntuneCD.update.update_enrollmentConfigurations.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.update_enrollmentConfigurations.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.update_assignment_patch = patch(
            "src.IntuneCD.update.update_enrollmentConfigurations.update_assignment"
        )
        self.update_assignment = self.update_assignment_patch.start()

        self.load_file_patch = patch(
            "src.IntuneCD.update.update_enrollmentConfigurations.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.post_assignment_update_patch = patch(
            "src.IntuneCD.update.update_enrollmentConfigurations.post_assignment_update"
        )
        self.post_assignment_update = self.post_assignment_update_patch.start()

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.update_enrollmentConfigurations.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update.update_enrollmentConfigurations.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update.update_enrollmentConfigurations.makeapirequestDelete"
        )
        self.makeapirequestDelete = self.makeapirequestDelete_patch.start()

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
        self.makeapirequestDelete.stop()

    def test_update_with_diffs_and_assignment(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_diffs_no_assignment(self):
        """The count should be 1 and the makeapirequestPatch should be called."""

        self.count = update(
            self.directory.path, self.token, assignment=False, remove=False
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_with_no_diffs_and_assignment(self):
        """The count should be 0, the post_assignment_update should be called,
        and makeapirequestPatch should not be called."""

        self.mem_data["value"][0]["platformRestriction"]["platformBlocked"] = False

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_no_diffs_no_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.mem_data["value"][0]["platformRestriction"]["platformBlocked"] = False

        self.count = update(
            self.directory.path, self.token, assignment=False, remove=False
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_priority(self):
        """The count should be 1 and the makeapirequestPost should be called."""

        self.repo_data["priority"] = 2

        self.count = update(
            self.directory.path, self.token, assignment=False, remove=False
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPost.call_count, 1)

    def test_update_config_not_found_and_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.mem_data["value"][0]["displayName"] = "test1"

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 2)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_config_not_found_iOS_and_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.mem_data["value"][0]["displayName"] = "test1"
        self.repo_data["platformType"] = "iOS"

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_config_not_found_limit_and_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.mem_data["value"][0]["displayName"] = "test1"
        self.repo_data["@odata.type"] = "#microsoft.graph.limit"

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_remove_config(self):
        """makeapirequestDelete should be called."""

        self.mem_data["value"].append(
            {"displayName": "test2", "id": "2", "@odata.type": "#microsoft.graph.limit"}
        )

        self.update = update(self.directory.path, self.token, report=False, remove=True)

        self.assertEqual(self.makeapirequestDelete.call_count, 1)


if __name__ == "__main__":
    unittest.main()
