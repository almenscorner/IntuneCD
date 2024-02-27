#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up App Configuration."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.Intune.backup_configurationPolicies import savebackup

BATCH_REQUEST = [
    {
        "@odata.context": "https://graph.microsoft.com/beta/$metadata#deviceManagement/configurationPolicies('0')/settings",
        "@odata.count": 2,
        "value": [
            {
                "id": "0",
                "settingInstance": {
                    "@odata.type": "#microsoft.graph.deviceManagementConfigurationChoiceSettingInstance",
                    "settingDefinitionId": "com.apple.managedclient.preferences_enforcementlevel",
                    "settingInstanceTemplateReference": None,
                    "choiceSettingValue": {
                        "settingValueTemplateReference": None,
                        "value": "com.apple.managedclient.preferences_enforcementlevel_0",
                        "children": [],
                    },
                },
            }
        ],
    }
]
BATCH_ASSIGNMENT = [{"value": [{"id": "0", "target": {"groupName": "Group1"}}]}]
OBJECT_ASSIGNMENT = [{"target": {"groupName": "Group1"}}]


class TestBackupConfigurationPolicy(unittest.TestCase):
    """Test class for backup_appConfiguration."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.append_id = False
        self.saved_path = f"{self.directory.path}/Settings Catalog/test_test."
        self.expected_data = {
            "@odata.type": "#microsoft.graph.deviceManagementConfigurationPolicy",
            "assignments": [{"target": {"groupName": "Group1"}}],
            "description": "Description value",
            "name": "test",
            "technologies": "test",
            "roleScopeTagIds": ["Role Scope Tag Ids value"],
            "settings": [
                {
                    "id": "0",
                    "settingInstance": {
                        "@odata.type": "#microsoft.graph.deviceManagementConfigurationChoiceSettingInstance",
                        "choiceSettingValue": {
                            "children": [],
                            "settingValueTemplateReference": None,
                            "value": "com.apple.managedclient.preferences_enforcementlevel_0",
                        },
                        "settingDefinitionId": "com.apple.managedclient.preferences_enforcementlevel",
                        "settingInstanceTemplateReference": None,
                    },
                }
            ],
            "templateReference": {
                "@odata.type": "microsoft.graph.deviceManagementConfigurationPolicyTemplateReference",
                "templateId": "Template Id value",
            },
        }
        self.configuration_policy = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.deviceManagementConfigurationPolicy",
                    "id": "0",
                    "name": "test",
                    "technologies": "test",
                    "description": "Description value",
                    "roleScopeTagIds": ["Role Scope Tag Ids value"],
                    "isAssigned": True,
                    "templateReference": {
                        "@odata.type": "microsoft.graph.deviceManagementConfigurationPolicyTemplateReference",
                        "templateId": "Template Id value",
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

        self.batch_assignment_patch = patch(
            "src.IntuneCD.backup.Intune.backup_configurationPolicies.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.batch_request_patch = patch(
            "src.IntuneCD.backup.Intune.backup_configurationPolicies.batch_request"
        )
        self.batch_request = self.batch_request_patch.start()
        self.batch_request.return_value = BATCH_REQUEST

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup.Intune.backup_configurationPolicies.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_configurationPolicies.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.configuration_policy

        self.makeAuditRequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_configurationPolicies.makeAuditRequest"
        )
        self.makeAuditRequest = self.makeAuditRequest_patch.start()
        self.makeAuditRequest.return_value = self.audit_data

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.batch_request.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()
        self.makeAuditRequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path,
            "yaml",
            self.exclude,
            self.token,
            "",
            self.append_id,
            False,
            None,
        )

        with open(self.saved_path + "yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            self.saved_data = json.loads(data)

        self.assertTrue(Path(f"{self.directory.path}/Settings Catalog").exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            "",
            self.append_id,
            False,
            None,
        )

        with open(self.saved_path + "json", "r", encoding="utf-8") as f:
            self.saved_data = json.load(f)

        self.assertTrue(Path(f"{self.directory.path}/Settings Catalog").exists())
        self.assertEqual(self.expected_data, self.saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_returned_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = {"value": []}
        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            "",
            self.append_id,
            False,
            None,
        )
        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = {"value": []}
        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
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
            self.directory.path, "json", self.exclude, self.token, "", True, False, None
        )

        self.assertTrue(
            Path(f"{self.directory.path}/Settings Catalog/test_test__0.json").exists()
        )

    def test_backup_scope_tag_and_audit(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            "",
            True,
            False,
            [{"id": 0, "displayName": "default"}],
        )

        self.assertTrue(
            Path(f"{self.directory.path}/Settings Catalog/test_test__0.json").exists()
        )
        self.assertEqual(1, self.count["config_count"])


if __name__ == "__main__":
    unittest.main()
