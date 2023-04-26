#!/usr/bin/env python3

"""This module tests updating Profiles."""

import unittest

from testfixtures import TempDirectory
from unittest.mock import patch
from src.IntuneCD.update_profiles import update


class TestUpdateCompliance(unittest.TestCase):
    """Test class for update_profiles."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Device Configurations")
        self.directory.write(
            "Device Configurations/test.json", '{"test": "test"}', encoding="utf-8"
        )
        self.directory.write(
            "Device Configurations/mobileconfig/test.mobileconfig",
            "test",
            encoding="utf - 8",
        )
        self.token = "token"
        self.mem_data_base = {
            "value": [
                {
                    "@odata.type": "test",
                    "id": "0",
                    "displayName": "test",
                    "testvalue": "test",
                    "assignments": [{"target": {"groupId": "test"}}],
                }
            ]
        }
        self.repo_data_base = {
            "@odata.type": "test",
            "id": "0",
            "displayName": "test",
            "testvalue": "test1",
            "assignments": [{"target": {"groupName": "test1"}}],
        }

        self.batch_assignment_patch = patch(
            "src.IntuneCD.update_profiles.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()

        self.object_assignment_patch = patch(
            "src.IntuneCD.update_profiles.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()

        self.makeapirequest_patch = patch("src.IntuneCD.update_profiles.makeapirequest")
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data_base

        self.update_assignment_patch = patch(
            "src.IntuneCD.update_profiles.update_assignment"
        )
        self.update_assignment = self.update_assignment_patch.start()

        self.load_file_patch = patch("src.IntuneCD.update_profiles.load_file")
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data_base

        self.post_assignment_update_patch = patch(
            "src.IntuneCD.update_profiles.post_assignment_update"
        )
        self.post_assignment_update = self.post_assignment_update_patch.start()

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update_profiles.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update_profiles.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

        self.plistlib_patch = patch("src.IntuneCD.update_profiles.plistlib")
        self.plistlib = self.plistlib_patch.start()
        self.plistlib.load.return_value = {"PayloadContent": [{"test": "test"}]}
        self.plistlib.dumps.return_value = b"test"

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update_profiles.makeapirequestDelete"
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
        self.plistlib.stop()
        self.makeapirequestDelete.stop()

    def test_update_custom_macOS_with_diffs_and_assignment(self):
        """The count should be 2 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_payload = {"PayloadContent": [{"test": "test1"}]}
        self.mem_payload = {"PayloadContent": [{"test": "test"}]}

        self.plistlib.load.side_effect = self.repo_payload, self.mem_payload

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.macOSCustomConfiguration"
        self.mem_data_base["value"][0][
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.mem_data_base["value"][0]["payloadFileName"] = "test.mobileconfig"

        self.repo_data_base["@odata.type"] = "#microsoft.graph.macOSCustomConfiguration"
        self.repo_data_base[
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.repo_data_base["payloadFileName"] = "test.mobileconfig"
        self.repo_data_base["payloadName"] = "test"

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_custom_macOS_with_diffs_no_assignment(self):
        """The count should be 2 and the makeapirequestPatch should be called."""

        self.repo_payload = {"PayloadContent": [{"test": "test1"}]}
        self.mem_payload = {"PayloadContent": [{"test": "test"}]}

        self.plistlib.load.side_effect = self.repo_payload, self.mem_payload

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.macOSCustomConfiguration"
        self.mem_data_base["value"][0][
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.mem_data_base["value"][0]["payloadFileName"] = "test.mobileconfig"
        self.repo_data_base["payloadName"] = "test"

        self.repo_data_base["@odata.type"] = "#microsoft.graph.macOSCustomConfiguration"
        self.repo_data_base[
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.repo_data_base["payloadFileName"] = "test.mobileconfig"

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_custom_macOS_with_no_diffs_and_assignment(self):
        """The count should be 0, the post_assignment_update should be called,
        and makeapirequestPatch should not be called."""

        self.repo_payload = {"PayloadContent": [{"test": "test"}]}
        self.mem_payload = {"PayloadContent": [{"test": "test"}]}
        self.repo_data_base["testvalue"] = "test"

        self.plistlib.load.side_effect = self.repo_payload, self.mem_payload

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.macOSCustomConfiguration"
        self.mem_data_base["value"][0][
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.mem_data_base["value"][0]["payloadFileName"] = "test.mobileconfig"
        self.repo_data_base["payloadName"] = "test"

        self.repo_data_base["@odata.type"] = "#microsoft.graph.macOSCustomConfiguration"
        self.repo_data_base[
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.repo_data_base["payloadFileName"] = "test.mobileconfig"

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_custom_macOS_with_no_diffs_no_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.repo_payload = {"PayloadContent": [{"test": "test"}]}
        self.mem_payload = {"PayloadContent": [{"test": "test"}]}
        self.repo_data_base["testvalue"] = "test"

        self.plistlib.load.side_effect = self.repo_payload, self.mem_payload

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.macOSCustomConfiguration"
        self.mem_data_base["value"][0][
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.mem_data_base["value"][0]["payloadFileName"] = "test.mobileconfig"

        self.repo_data_base["@odata.type"] = "#microsoft.graph.macOSCustomConfiguration"
        self.repo_data_base[
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.repo_data_base["payloadFileName"] = "test.mobileconfig"
        self.repo_data_base["payloadName"] = "test"

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_custom_iOS_with_diffs_and_assignment(self):
        """The count should be 2 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_payload = {"PayloadContent": [{"test": "test1"}]}
        self.mem_payload = {"PayloadContent": [{"test": "test"}]}

        self.plistlib.load.side_effect = self.repo_payload, self.mem_payload

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.iosCustomConfiguration"
        self.mem_data_base["value"][0][
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.mem_data_base["value"][0]["payloadFileName"] = "test.mobileconfig"

        self.repo_data_base["@odata.type"] = "#microsoft.graph.iosCustomConfiguration"
        self.repo_data_base[
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.repo_data_base["payloadFileName"] = "test.mobileconfig"
        self.repo_data_base["payloadName"] = "test"

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_custom_iOS_with_diffs_no_assignment(self):
        """The count should be 1 and the makeapirequestPatch should be called."""

        self.repo_payload = {"PayloadContent": [{"test": "test1"}]}
        self.mem_payload = {"PayloadContent": [{"test": "test"}]}

        self.plistlib.load.side_effect = self.repo_payload, self.mem_payload

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.iosCustomConfiguration"
        self.mem_data_base["value"][0][
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.mem_data_base["value"][0]["payloadFileName"] = "test.mobileconfig"

        self.repo_data_base["@odata.type"] = "#microsoft.graph.iosCustomConfiguration"
        self.repo_data_base[
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.repo_data_base["payloadFileName"] = "test.mobileconfig"
        self.repo_data_base["payloadName"] = "test"

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_custom_iOS_with_no_diffs_and_assignment(self):
        """The count should be 0, the post_assignment_update should be called,
        and makeapirequestPatch should not be called."""

        self.repo_payload = {"PayloadContent": [{"test": "test"}]}
        self.mem_payload = {"PayloadContent": [{"test": "test"}]}
        self.repo_data_base["testvalue"] = "test"

        self.plistlib.load.side_effect = self.repo_payload, self.mem_payload

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.iosCustomConfiguration"
        self.mem_data_base["value"][0][
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.mem_data_base["value"][0]["payloadFileName"] = "test.mobileconfig"

        self.repo_data_base["@odata.type"] = "#microsoft.graph.iosCustomConfiguration"
        self.repo_data_base[
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.repo_data_base["payloadFileName"] = "test.mobileconfig"
        self.repo_data_base["payloadName"] = "test"

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_custom_iOS_with_no_diffs_no_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.repo_payload = {"PayloadContent": [{"test": "test"}]}
        self.mem_payload = {"PayloadContent": [{"test": "test"}]}
        self.repo_data_base["testvalue"] = "test"

        self.plistlib.load.side_effect = self.repo_payload, self.mem_payload

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.iosCustomConfiguration"
        self.mem_data_base["value"][0][
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.mem_data_base["value"][0]["payloadFileName"] = "test.mobileconfig"

        self.repo_data_base["@odata.type"] = "#microsoft.graph.iosCustomConfiguration"
        self.repo_data_base[
            "payload"
        ] = "T29vIHllYWgsIGl0J3MgZ29ubmEgd29yaywgSSBwcm9taXNl"
        self.repo_data_base["payloadFileName"] = "test.mobileconfig"
        self.repo_data_base["payloadName"] = "test"

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_custom_windows_with_diffs_and_assignment(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.windows10CustomConfiguration"
        self.mem_data_base["value"][0]["omaSettings"] = [
            {
                "isEncrypted": True,
                "@odata.type": "#microsoft.graph.windows10OmaSetting",
                "secretReferenceValueId": "0",
                "omaUri": "test uri",
                "displayName": "test",
                "description": "",
                "value": {},
            }
        ]

        self.oma_values = {
            "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
            "value": "password",
        }

        self.repo_data_base[
            "@odata.type"
        ] = "#microsoft.graph.windows10CustomConfiguration"
        self.repo_data_base["omaSettings"] = [
            {
                "isEncrypted": True,
                "@odata.type": "#microsoft.graph.windows10OmaSetting",
                "secretReferenceValueId": "0",
                "omaUri": "test uri",
                "displayName": "test",
                "description": "",
                "value": {
                    "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
                    "value": "password2",
                },
            }
        ]

        self.makeapirequest.side_effect = self.mem_data_base, self.oma_values

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_custom_windows_with_diffs_no_assignment(self):
        """The count should be 1 and the makeapirequestPatch should be called."""

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.windows10CustomConfiguration"
        self.mem_data_base["value"][0]["omaSettings"] = [
            {
                "isEncrypted": True,
                "@odata.type": "#microsoft.graph.windows10OmaSetting",
                "secretReferenceValueId": "0",
                "omaUri": "test uri",
                "displayName": "test",
                "description": "",
                "value": {},
            }
        ]

        self.oma_values = {
            "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
            "value": "password",
        }

        self.repo_data_base[
            "@odata.type"
        ] = "#microsoft.graph.windows10CustomConfiguration"
        self.repo_data_base["omaSettings"] = [
            {
                "isEncrypted": True,
                "@odata.type": "#microsoft.graph.windows10OmaSetting",
                "secretReferenceValueId": "0",
                "omaUri": "test uri",
                "displayName": "test",
                "description": "",
                "value": {
                    "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
                    "value": "password2",
                },
            }
        ]

        self.makeapirequest.side_effect = self.mem_data_base, self.oma_values

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_custom_windows_no_diffs_and_assignment(self):
        """The count should be 0, the post_assignment_update should be called,
        and makeapirequestPatch should not be called."""

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.windows10CustomConfiguration"
        self.mem_data_base["value"][0]["omaSettings"] = [
            {
                "isEncrypted": True,
                "@odata.type": "#microsoft.graph.windows10OmaSetting",
                "secretReferenceValueId": "0",
                "omaUri": "test uri",
                "displayName": "test",
                "description": "",
                "value": {},
            }
        ]

        self.oma_values = {
            "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
            "value": "password",
        }

        self.repo_data_base[
            "@odata.type"
        ] = "#microsoft.graph.windows10CustomConfiguration"
        self.repo_data_base["omaSettings"] = [
            {
                "isEncrypted": True,
                "@odata.type": "#microsoft.graph.windows10OmaSetting",
                "secretReferenceValueId": "0",
                "omaUri": "test uri",
                "displayName": "test",
                "description": "",
                "value": {
                    "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
                    "value": "password",
                },
            }
        ]

        self.makeapirequest.side_effect = self.mem_data_base, self.oma_values

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_custom_windows_no_diffs_no_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.windows10CustomConfiguration"
        self.mem_data_base["value"][0]["omaSettings"] = [
            {
                "isEncrypted": True,
                "@odata.type": "#microsoft.graph.windows10OmaSetting",
                "secretReferenceValueId": "0",
                "omaUri": "test uri",
                "displayName": "test",
                "description": "",
                "value": {},
            }
        ]

        self.oma_values = {
            "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
            "value": "password",
        }

        self.repo_data_base[
            "@odata.type"
        ] = "#microsoft.graph.windows10CustomConfiguration"
        self.repo_data_base["omaSettings"] = [
            {
                "isEncrypted": True,
                "@odata.type": "#microsoft.graph.windows10OmaSetting",
                "secretReferenceValueId": "0",
                "omaUri": "test uri",
                "displayName": "test",
                "description": "",
                "value": {
                    "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
                    "value": "password",
                },
            }
        ]

        self.makeapirequest.side_effect = self.mem_data_base, self.oma_values

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_other_with_diffs_and_assignment(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.macOSConfiguration"

        self.repo_data_base["@odata.type"] = "#microsoft.graph.macOSConfiguration"

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_other_with_diffs_no_assignment(self):
        """The count should be 1 and the makeapirequestPatch should be called."""

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.macOSConfiguration"

        self.repo_data_base["@odata.type"] = "#microsoft.graph.macOSConfiguration"

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_other_no_diffs_and_assignment(self):
        """The count should be 0, the post_assignment_update should be called,
        and makeapirequestPatch should not be called."""

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.macOSConfiguration"
        self.mem_data_base["value"][0]["testvalue"] = "test1"

        self.repo_data_base["@odata.type"] = "#microsoft.graph.macOSConfiguration"

        self.count = update(self.directory.path, self.token, assignment=True)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_other_no_diffs_no_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.mem_data_base["value"][0][
            "@odata.type"
        ] = "#microsoft.graph.macOSConfiguration"
        self.mem_data_base["value"][0]["testvalue"] = "test1"

        self.repo_data_base["@odata.type"] = "#microsoft.graph.macOSConfiguration"

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_config_not_found_and_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.mem_data_base["value"][0]["displayName"] = "test1"

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_custom_windows_config_not_found_and_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.mem_data_base["value"][0]["displayName"] = "test1"

        self.repo_data_base[
            "@odata.type"
        ] = "#microsoft.graph.windows10CustomConfiguration"
        self.repo_data_base["omaSettings"] = [
            {
                "isEncrypted": True,
                "@odata.type": "#microsoft.graph.windows10OmaSetting",
                "secretReferenceValueId": "0",
                "omaUri": "test uri",
                "displayName": "test",
                "description": "",
                "value": {
                    "@odata.context": "https://graph.microsoft.com/beta/$metadata#Edm.String",
                    "value": "password2",
                },
            }
        ]

        self.count = update(self.directory.path, self.token, assignment=False)

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)


if __name__ == "__main__":
    unittest.main()
