#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests updating Reusable Policy Settings."""

import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Intune.update_reusablePolicySettings import update


@patch("time.sleep", return_value=None)
class TestUpdateReusablePolicySettings(unittest.TestCase):
    """Test class for update_reusablePolicySettings."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Compliance Policies/Scripts")
        self.directory.makedir("Compliance Policies/Scripts/Script Data")
        self.directory.write(
            "Compliance Policies/Scripts/test.json",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.directory.write(
            "Compliance Policies/Scripts/Script Data/test.sh",
            "You found a secret message, hooray!",
            encoding="utf-8",
        )
        self.token = "token"
        self.mem_script_content = "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2Us"
        self.repo_script_content = "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2UsIGhvb3JheSE="
        self.mem_detectionScript_data = {
            "value": [
                {
                    "@odata.type": "test",
                    "id": "0",
                    "displayName": "test",
                    "testvalue": "test",
                    "detectionScriptContent": self.mem_script_content,
                }
            ]
        }
        self.mem_data = {
            "value": [
                {
                    "displayName": "test",
                    "description": "",
                    "id": "0",
                    "settingDefinitionId": "linux_customcompliance_discoveryscript_reusablesetting",
                    "settingInstance": {
                        "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
                        "settingDefinitionId": "linux_customcompliance_discoveryscript_reusablesetting",
                        "settingInstanceTemplateReference": None,
                        "simpleSettingValue": {
                            "@odata.type": "#microsoft.graph.deviceManagementConfigurationStringSettingValue",
                            "settingValueTemplateReference": None,
                            "value": self.mem_script_content,
                        },
                    },
                }
            ]
        }
        self.repo_data = {
            "displayName": "test",
            "description": "",
            "settingDefinitionId": "linux_customcompliance_discoveryscript_reusablesetting",
            "settingInstance": {
                "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
                "settingDefinitionId": "linux_customcompliance_discoveryscript_reusablesetting",
                "settingInstanceTemplateReference": None,
                "simpleSettingValue": {
                    "@odata.type": "#microsoft.graph.deviceManagementConfigurationStringSettingValue",
                    "settingValueTemplateReference": None,
                    "value": self.repo_script_content,
                },
            },
        }

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Intune.update_reusablePolicySettings.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.side_effect = [self.mem_data, self.mem_data["value"][0]]

        self.load_file_patch = patch(
            "src.IntuneCD.update.Intune.update_reusablePolicySettings.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPut_patch = patch(
            "src.IntuneCD.update.Intune.update_reusablePolicySettings.makeapirequestPut"
        )
        self.makeapirequestPut = self.makeapirequestPut_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update.Intune.update_reusablePolicySettings.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update.Intune.update_reusablePolicySettings.makeapirequestDelete"
        )
        self.makeapirequestDelete = self.makeapirequestDelete_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest.stop()
        self.load_file.stop()
        self.makeapirequestPut.stop()
        self.makeapirequestPost.stop()
        self.makeapirequestDelete.stop()

    def test_update_with_diffs(self, _):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_data["description"] = "test1"
        self.makeapirequest.side_effect = [self.mem_data, self.mem_data["value"][0]]

        self.count = update(self.directory.path, self.token, report=False, remove=False)

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPut.call_count, 1)

    def test_update_with_no_diffs(self, _):
        """The count should be 0, the post_assignment_update should be called,
        and makeapirequestPatch should not be called."""

        self.mem_data["value"][0]["settingInstance"]["simpleSettingValue"][
            "value"
        ] = self.repo_script_content

        self.makeapirequest.side_effect = [self.mem_data, self.mem_data["value"][0]]

        self.count = update(self.directory.path, self.token, report=False, remove=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPut.call_count, 0)

    def test_update_config_not_found(self, _):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.repo_data["displayName"] = "test2"

        self.count = update(self.directory.path, self.token, report=False, remove=False)

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)

    def test_remove_config(self, _):
        """makeapirequestDelete should be called."""

        self.mem_data["value"].append({"displayName": "test2", "id": "2"})
        self.makeapirequest.side_effect = [self.mem_data, self.mem_data["value"][0]]

        self.update = update(self.directory.path, self.token, report=False, remove=True)

        self.assertEqual(self.makeapirequestDelete.call_count, 1)

    def test_update_config_no_settingDefinitionId(self, _):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.repo_data.pop("settingDefinitionId")

        self.count = update(self.directory.path, self.token, report=False, remove=False)

        self.assertEqual(self.count, [])


if __name__ == "__main__":
    unittest.main()
