#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests backing up compliance."""

import json
import os.path
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.backup.Intune.backup_compliancePolicies import savebackup

BATCH_ASSIGNMENT = [{"value": [{"id": "0", "target": {"groupName": "Group1"}}]}]
OBJECT_ASSIGNMENT = [{"target": {"groupName": "Group1"}}]


class TestBackupCompliance(unittest.TestCase):
    """Test class for backup_compliance."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.exclude = []
        self.append_id = False
        self.saved_path = (
            f"{self.directory.path}/Compliance Policies/Policies/test_linuxMdm."
        )
        self.expected_data = {
            "roleScopeTagIds": ["0"],
            "description": "Description value",
            "name": "test",
            "technologies": "linuxMdm",
            "detectionScriptName": "test",
            "settings": [
                {
                    "id": "0",
                    "settingInstance": {
                        "@odata.type": "#microsoft.graph.deviceManagementConfigurationChoiceSettingInstance",
                        "settingDefinitionId": "linux_customcompliance_required",
                        "settingInstanceTemplateReference": None,
                        "choiceSettingValue": {
                            "settingValueTemplateReference": None,
                            "value": "linux_customcompliance_required_true",
                            "children": [
                                {
                                    "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
                                    "settingDefinitionId": "linux_customcompliance_discoveryscript",
                                    "settingInstanceTemplateReference": None,
                                    "simpleSettingValue": {
                                        "@odata.type": "#microsoft.graph.deviceManagementConfigurationReferenceSettingValue",
                                        "settingValueTemplateReference": None,
                                        "value": "ea75ed9d-2df4-4977-8eb7-340c837ed5ee",
                                        "note": None,
                                    },
                                }
                            ],
                        },
                    },
                }
            ],
            "scheduledActionsForRule": [
                {
                    "ruleName": None,
                    "scheduledActionConfigurations": [{"gracePeriodHours": 0}],
                }
            ],
            "assignments": [{"target": {"groupName": "Group1"}}],
        }
        self.compliance_policy = {
            "value": [
                {
                    "roleScopeTagIds": ["0"],
                    "description": "Description value",
                    "name": "test",
                    "id": "0",
                    "technologies": "linuxMdm",
                    "settings": [
                        {
                            "id": "0",
                            "settingInstance": {
                                "@odata.type": "#microsoft.graph.deviceManagementConfigurationChoiceSettingInstance",
                                "settingDefinitionId": "linux_customcompliance_required",
                                "settingInstanceTemplateReference": None,
                                "choiceSettingValue": {
                                    "settingValueTemplateReference": None,
                                    "value": "linux_customcompliance_required_true",
                                    "children": [
                                        {
                                            "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
                                            "settingDefinitionId": "linux_customcompliance_discoveryscript",
                                            "settingInstanceTemplateReference": None,
                                            "simpleSettingValue": {
                                                "@odata.type": "#microsoft.graph.deviceManagementConfigurationReferenceSettingValue",
                                                "settingValueTemplateReference": None,
                                                "value": "ea75ed9d-2df4-4977-8eb7-340c837ed5ee",
                                                "note": None,
                                            },
                                        }
                                    ],
                                },
                            },
                        }
                    ],
                    "scheduledActionsForRule": [
                        {
                            "ruleName": None,
                            "scheduledActionConfigurations": [{"gracePeriodHours": 0}],
                        }
                    ],
                    "assignments": [{"target": {"groupName": "Group1"}}],
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
        self.scheduled_actions = {
            "value": [
                {
                    "ruleName": None,
                    "scheduledActionConfigurations": [{"gracePeriodHours": 0}],
                }
            ]
        }
        self.batch_assignment_patch = patch(
            "src.IntuneCD.backup.Intune.backup_compliancePolicies.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()
        self.batch_assignment.return_value = BATCH_ASSIGNMENT

        self.object_assignment_patch = patch(
            "src.IntuneCD.backup.Intune.backup_compliancePolicies.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()
        self.object_assignment.return_value = OBJECT_ASSIGNMENT

        self.makeapirequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_compliancePolicies.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.side_effect = [
            self.compliance_policy,
            {"value": [{"id": 0, "displayName": "test"}]},
            self.scheduled_actions,
        ]

        self.makeAuditRequest_patch = patch(
            "src.IntuneCD.backup.Intune.backup_compliancePolicies.makeAuditRequest"
        )
        self.makeAuditRequest = self.makeAuditRequest_patch.start()
        self.makeAuditRequest.return_value = self.audit_data

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment.stop()
        self.object_assignment.stop()
        self.makeapirequest.stop()
        self.makeAuditRequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        output = "yaml"
        count = savebackup(
            self.directory.path,
            output,
            self.exclude,
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
            Path(f"{self.directory.path}/Compliance Policies/Policies").exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        output = "json"
        count = savebackup(
            self.directory.path,
            output,
            self.exclude,
            self.token,
            "",
            self.append_id,
            False,
            None,
        )

        with open(self.saved_path + output, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertTrue(
            Path(f"{self.directory.path}/Compliance Policies/Policies").exists()
        )
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, count["config_count"])

    def test_backup_with_no_returned_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.side_effect = [
            {"value": []},
            {"value": [{"id": 0, "displayName": "test"}]},
            self.scheduled_actions,
        ]
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
        self.assertEqual(1, self.count["config_count"])
        self.assertTrue(
            os.path.exists(
                f"{self.directory.path}/Compliance Policies/Policies/test_linuxMdm.json"
            )
        )

    def test_backup_with_prefix_no_match(self):
        """The count should be 0 if no data is returned."""

        self.compliance_policy["value"][0]["name"] = "linuxCompliancePolicy"
        self.makeapirequest.side_effect = [
            self.compliance_policy,
            {"value": [{"id": 0, "displayName": "test"}]},
            self.scheduled_actions,
        ]

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
            Path(
                f"{self.directory.path}/Compliance Policies/Policies/test_linuxMdm__0.json"
            ).exists()
        )

    def test_backup_scope_tags_and_audit(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(
            self.directory.path,
            "json",
            self.exclude,
            self.token,
            "",
            True,
            True,
            [{"id": 0, "displayName": "default"}],
        )

        self.assertTrue(
            Path(
                f"{self.directory.path}/Compliance Policies/Policies/test_linuxMdm__0.json"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
