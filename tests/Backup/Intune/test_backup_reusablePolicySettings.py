#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up Reusable Policy Settings."""

import json
import os.path
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.Intune.backup_reusablePolicySettings import savebackup


class TestBackupReusablePolicySettings(unittest.TestCase):
    """Test class for backup_reusablePolicySettings."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.append_id = False
        self.saved_path = f"{self.directory.path}/Compliance Policies/Scripts/testsh."
        self.expected_data = {
            "displayName": "testsh",
            "description": "",
            "settingDefinitionId": "linux_customcompliance_discoveryscript_reusablesetting",
            "settingInstance": {
                "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
                "settingDefinitionId": "linux_customcompliance_discoveryscript_reusablesetting",
                "settingInstanceTemplateReference": None,
                "simpleSettingValue": {
                    "@odata.type": "#microsoft.graph.deviceManagementConfigurationStringSettingValue",
                    "settingValueTemplateReference": None,
                    "value": "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2UsIGhvb3JheSE=",
                },
            },
        }
        self.reusable_policy_settings_policy_script = {
            "value": [
                {
                    "id": "0",
                    "displayName": "testsh",
                    "description": "",
                    "settingDefinitionId": "linux_customcompliance_discoveryscript_reusablesetting",
                    "settingInstance": {
                        "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
                        "settingDefinitionId": "linux_customcompliance_discoveryscript_reusablesetting",
                        "settingInstanceTemplateReference": None,
                        "simpleSettingValue": {
                            "@odata.type": "#microsoft.graph.deviceManagementConfigurationStringSettingValue",
                            "settingValueTemplateReference": None,
                            "value": "WW91IGZvdW5kIGEgc2VjcmV0IG1lc3NhZ2UsIGhvb3JheSE=",
                        },
                    },
                }
            ]
        }
        self.audit_data = {
            "value": [
                {
                    "resources": [
                        {"resourceId": "0", "auditResourceType": "MagicResource"}
                    ],
                    "activityDateTime": "2021-01-01T00:00:00Z",
                    "activityOperationType": "Patch",
                    "activityResult": "Success",
                    "actor": [{"auditActorType": "ItPro"}],
                }
            ]
        }

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_reusablePolicySettings.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.side_effect = [
            self.reusable_policy_settings_policy_script,
            self.reusable_policy_settings_policy_script["value"][0],
        ]

        self.makeAuditRequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_reusablePolicySettings.makeAuditRequest"
        )
        self.makeAuditRequest = self.makeAuditRequest_patch.start()
        self.makeAuditRequest.return_value = self.audit_data

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest.stop()
        self.makeAuditRequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        output = "yaml"
        count = savebackup(
            self.directory.path,
            output,
            self.token,
            "",
            self.append_id,
            False,
            None,
        )

        with open(self.saved_path + output, "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(
            Path(f"{self.directory.path}/Compliance Policies/Scripts").exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        output = "json"
        count = savebackup(
            self.directory.path,
            output,
            self.token,
            "",
            self.append_id,
            False,
            None,
        )

        with open(self.saved_path + output, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertTrue(
            Path(f"{self.directory.path}/Compliance Policies/Scripts").exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, count["config_count"])

    def test_backup_with_no_returned_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.side_effect = [{"value": []}]
        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            "",
            self.append_id,
            False,
            None,
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if no data is returned."""

        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            "test",
            self.append_id,
            False,
            None,
        )
        self.assertEqual(1, self.count["config_count"])
        self.assertTrue(
            os.path.exists(
                f"{self.directory.path}/Compliance Policies/Scripts/testsh.json"
            )
        )

    def test_backup_with_prefix_no_match(self):
        """The count should be 0 if no data is returned."""

        self.reusable_policy_settings_policy_script["value"][0][
            "displayName"
        ] = "notTestScript"
        self.makeapirequest.side_effect = [
            self.reusable_policy_settings_policy_script,
            self.reusable_policy_settings_policy_script["value"][0],
        ]
        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            "test",
            self.append_id,
            False,
            None,
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_append_id(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path, "json", self.token, "", True, False, None
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Compliance Policies/Scripts/testsh__0.json"
            ).exists()
        )

    def test_backup_scope_tags_and_audit(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path,
            "json",
            self.token,
            "",
            True,
            True,
            [{"id": 0, "displayName": "default"}],
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Compliance Policies/Scripts/testsh__0.json"
            ).exists()
        )

    def test_backup_no_settingDefinitionId(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.reusable_policy_settings_policy_script["value"][0].pop(
            "settingDefinitionId"
        )
        self.makeapirequest.side_effect = [
            self.reusable_policy_settings_policy_script,
            self.reusable_policy_settings_policy_script["value"][0],
        ]
        self.count = savebackup(
            self.directory.path, "json", self.token, "", True, False, None
        )

        self.assertEqual(0, self.count["config_count"])


if __name__ == "__main__":
    unittest.main()
