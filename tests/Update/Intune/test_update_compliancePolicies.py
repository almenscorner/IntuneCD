#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module tests updating Compliance Policies."""

import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Intune.update_compliancePolicies import update


class TestUpdateCompliancePolicies(unittest.TestCase):
    """Test class for update_compliancePolicies."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Compliance Policies")
        self.directory.write(
            "Compliance Policies/Policies/test.json",
            '{"test": "test"}',
            encoding="utf-8",
        )
        self.directory.write(
            "Compliance Policies/Policies/test.txt", "txt", encoding="utf-8"
        )
        self.token = "token"
        self.mem_data = {
            "value": [
                {
                    "creationSource": None,
                    "id": "0",
                    "description": "",
                    "name": "test",
                    "platforms": "linux",
                    "roleScopeTagIds": ["Default"],
                    "settingCount": 1,
                    "technologies": "linuxMdm",
                    "settings@odata.context": "https://graph.microsoft.com/beta/$metadata#deviceManagement/compliancePolicies('15db4b21-d2a4-41f2-aa53-7267f6ba6a7e')/settings",
                    "settings": [
                        {
                            "id": "0",
                            "settingInstance": {
                                "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
                                "settingDefinitionId": "linux_passwordpolicy_minimumdigits",
                                "settingInstanceTemplateReference": None,
                                "simpleSettingValue": {
                                    "@odata.type": "#microsoft.graph.deviceManagementConfigurationIntegerSettingValue",
                                    "settingValueTemplateReference": None,
                                    "value": 1,
                                },
                            },
                        }
                    ],
                }
            ]
        }
        self.repo_data = {
            "creationSource": None,
            "description": "",
            "name": "test",
            "platforms": "linux",
            "roleScopeTagIds": ["Default"],
            "settingCount": 1,
            "technologies": "linuxMdm",
            "settings@odata.context": "https://graph.microsoft.com/beta/$metadata#deviceManagement/compliancePolicies('15db4b21-d2a4-41f2-aa53-7267f6ba6a7e')/settings",
            "settings": [
                {
                    "id": "0",
                    "settingInstance": {
                        "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
                        "settingDefinitionId": "linux_passwordpolicy_minimumdigits",
                        "settingInstanceTemplateReference": None,
                        "simpleSettingValue": {
                            "@odata.type": "#microsoft.graph.deviceManagementConfigurationIntegerSettingValue",
                            "settingValueTemplateReference": None,
                            "value": 2,
                        },
                    },
                }
            ],
            "scheduledActionsForRule": [
                {
                    "ruleName": None,
                    "scheduledActionConfigurations": [
                        {
                            "gracePeriodHours": 0,
                            "actionType": "block",
                            "notificationTemplateId": "00000000-0000-0000-0000-000000000000",
                            "notificationMessageCCList": [],
                        }
                    ],
                }
            ],
            "assignments": [
                {
                    "source": "direct",
                    "target": {
                        "@odata.type": "#microsoft.graph.groupAssignmentTarget",
                        "deviceAndAppManagementAssignmentFilterId": None,
                        "deviceAndAppManagementAssignmentFilterType": "none",
                        "groupName": "Department 2",
                        "groupType": "StaticMembership",
                    },
                }
            ],
        }
        self.script_settings = {
            "id": "0",
            "roleScopeTagIds": ["Default"],
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
                                "value": "33d9b35d-0bc5-4ba1-ada4-139d97b2f756",
                                "note": None,
                            },
                        },
                        {
                            "@odata.type": "#microsoft.graph.deviceManagementConfigurationSimpleSettingInstance",
                            "settingDefinitionId": "linux_customcompliance_rules",
                            "settingInstanceTemplateReference": None,
                            "simpleSettingValue": {
                                "@odata.type": "#microsoft.graph.deviceManagementConfigurationStringSettingValue",
                                "settingValueTemplateReference": None,
                                "value": "ewogICAgIlJ1bGVzIjpbIAogICAgICAgIHsgCiAgICAgICAgICAgIlNldHRpbmdOYW1lIjoidGVzdCIsCiAgICAgICAgIHsKXQogICAgfQ==",
                            },
                        },
                    ],
                },
            },
        }

        self.batch_assignment_patch = patch(
            "src.IntuneCD.update.Intune.update_compliancePolicies.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()

        self.object_assignment_patch = patch(
            "src.IntuneCD.update.Intune.update_compliancePolicies.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Intune.update_compliancePolicies.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.update_assignment_patch = patch(
            "src.IntuneCD.update.Intune.update_compliancePolicies.update_assignment"
        )
        self.update_assignment = self.update_assignment_patch.start()

        self.load_file_patch = patch(
            "src.IntuneCD.update.Intune.update_compliancePolicies.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.post_assignment_update_patch = patch(
            "src.IntuneCD.update.Intune.update_compliancePolicies.post_assignment_update"
        )
        self.post_assignment_update = self.post_assignment_update_patch.start()

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Intune.update_compliancePolicies.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update.Intune.update_compliancePolicies.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update.Intune.update_compliancePolicies.makeapirequestDelete"
        )
        self.makeapirequestDelete = self.makeapirequestDelete_patch.start()

        self.makeapirequestPut_patch = patch(
            "src.IntuneCD.update.Intune.update_compliancePolicies.makeapirequestPut"
        )
        self.makeapirequestPut = self.makeapirequestPut_patch.start()

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
        self.makeapirequestPut.stop()

    def test_update_with_diffs_and_assignment(self):
        """The count should be 2 and the post_assignment_update and makeapirequestPatch should be called."""

        self.repo_data["scheduledActionsForRule"][0]["scheduledActionConfigurations"][
            0
        ]["gracePeriodHours"] = 0
        self.repo_data["description"] = "test1"

        self.makeapirequest.side_effect = [
            self.mem_data,
            {
                "value": [
                    {
                        "id": "1",
                        "scheduledActionConfigurations": [
                            {
                                "id": "cffdcc1f-400f-400b-a7f9-3a2fb63412f8",
                                "gracePeriodHours": 1,
                                "actionType": "block",
                                "notificationTemplateId": "00000000-0000-0000-0000-000000000000",
                                "notificationMessageCCList": [],
                            }
                        ],
                    }
                ]
            },
        ]

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False, report=False
        )

        self.assertEqual(self.count[0].count, 3)
        self.assertEqual(self.makeapirequestPut.call_count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_diffs_no_assignment(self):
        """The count should be 2 and the makeapirequestPatch should be called."""

        self.count = update(
            self.directory.path, self.token, assignment=False, remove=True
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPut.call_count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_with_no_diffs_and_assignment(self):
        """The count should be 0, the post_assignment_update should be called,
        and makeapirequestPatch should not be called."""

        self.mem_data["value"][0]["settings"][0]["settingInstance"][
            "simpleSettingValue"
        ]["value"] = 2

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=True
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPut.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_update_with_no_diffs_no_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.mem_data["value"][0]["settings"][0]["settingInstance"][
            "simpleSettingValue"
        ]["value"] = 2

        self.count = update(
            self.directory.path, self.token, assignment=False, remove=True
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPut.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_config_not_found_and_assignment(self):
        """The count should be 0, the post_assignment_update and makeapirequestPost should be called."""

        self.repo_data["name"] = "test1"

        self.count = update(
            self.directory.path, self.token, assignment=True, remove=False
        )

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 2)
        self.assertEqual(self.post_assignment_update.call_count, 1)

    def test_remove_config(self):
        """makeapirequestDelete should be called."""

        self.mem_data["value"][0]["name"] = "test1"

        self.update = update(self.directory.path, self.token, report=False, remove=True)

        self.assertEqual(self.makeapirequestDelete.call_count, 1)

    def test_update_with_detection_script(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.repo_data["detectionScriptName"] = "test1"
        self.repo_data["description"] = "test1"
        self.repo_data["settings"] = [self.script_settings]
        self.mem_data["value"][0]["settings"][0]["settingInstance"][
            "simpleSettingValue"
        ]["value"] = 2

        self.makeapirequest.side_effect = [
            self.mem_data,
            {"value": [{"displayName": "test1", "id": "0"}]},
            {
                "value": [
                    {
                        "id": "1",
                        "scheduledActionConfigurations": [
                            {
                                "id": "cffdcc1f-400f-400b-a7f9-3a2fb63412f8",
                                "gracePeriodHours": 1,
                                "actionType": "block",
                                "notificationTemplateId": "00000000-0000-0000-0000-000000000000",
                                "notificationMessageCCList": [],
                            }
                        ],
                    }
                ]
            },
            {"value": [{"displayName": "test1", "id": "0"}]},
        ]

        self.count = update(
            self.directory.path, self.token, assignment=False, remove=True
        )

        self.assertEqual(self.count[0].count, 2)
        self.assertEqual(self.makeapirequestPut.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_with_detection_script_not_found(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.repo_data["name"] = "test1"
        self.repo_data["detectionScriptName"] = "test1"
        self.repo_data["settings"] = [self.script_settings]
        self.makeapirequest.return_value = {"value": []}

        self.count = update(
            self.directory.path, self.token, assignment=False, remove=True
        )

        self.assertEqual(self.makeapirequestPost.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_with_detection_script_not_found_update(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        # self.repo_data["name"] = "test1"
        self.repo_data["detectionScriptName"] = "test1"
        self.repo_data["settings"] = [self.script_settings]
        self.makeapirequest.side_effect = [
            self.mem_data,
            {"value": [{"displayName": "test1", "id": "0"}]},
            {"value": []},
        ]

        self.count = update(
            self.directory.path, self.token, assignment=False, remove=True
        )

        self.assertEqual(self.makeapirequestPost.call_count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 0)

    def test_update_no_technology(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""

        self.repo_data.pop("technologies")

        self.count = update(
            self.directory.path, self.token, assignment=False, remove=True
        )

        self.assertEqual(self.count, [])

    def test_update_with_scope_tags(self):
        """The count should be 0, the post_assignment_update and makeapirequestPatch should not be called."""
        self.mem_data["value"][0]["settings"][0]["settingInstance"][
            "simpleSettingValue"
        ]["value"] = 2

        self.count = update(
            self.directory.path,
            self.token,
            assignment=False,
            remove=True,
            scope_tags=[{"id": "0", "displayName": "test"}],
        )

        self.assertEqual(self.count[0].count, 0)


if __name__ == "__main__":
    unittest.main()
