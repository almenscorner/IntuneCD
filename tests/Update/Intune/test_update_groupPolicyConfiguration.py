#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Intune.update_groupPolicyConfiguration import update


class TestUpdateGroupPolicyConfiguration(unittest.TestCase):
    """Test class for update_groupPolicyConfiguration."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Group Policy Configurations")
        self.directory.write(
            "Group Policy Configurations/Group Policy Configuration.json",
            '{"id": "test"}',
            encoding="utf-8",
        )
        self.token = "token"
        self.presentation_value = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.groupPolicyPresentationValueList",
                    "values": ["test"],
                    "id": "test",
                    "presentation": {
                        "id": "test",
                        "label": "test",
                        "@odata.type": "@odata.type': '#microsoft.graph.groupPolicyPresentationListBox",
                    },
                }
            ]
        }
        self.definition_value = {
            "value": [
                {
                    "enabled": True,
                    "configurationType": "Policy",
                    "id": "test",
                    "definition": {
                        "id": "test",
                        "displayName": "test",
                    },
                    "presentationValues": [],
                }
            ]
        }
        self.mem_data_base = {
            "value": [
                {
                    "id": "test",
                    "displayName": "test",
                    "description": "test",
                    "definitionValues": [],
                    "policyConfigurationIngestionType": "BuiltIn",
                    "assignments": [{"target": {"groupName": "test"}}],
                }
            ]
        }

        self.repo_data_base = {
            "id": "test",
            "displayName": "test",
            "description": "test1",
            "roleScopeTagIds": ["1"],
            "policyConfigurationIngestionType": "BuiltIn",
            "definitionValues": [
                {
                    "enabled": False,
                    "configurationType": "Policy",
                    "id": "test",
                    "definition": {
                        "id": "test",
                        "displayName": "test",
                    },
                    "presentationValues": [
                        {
                            "@odata.type": "#microsoft.graph.groupPolicyPresentationValueList",
                            "values": ["test1"],
                            "presentation": {
                                "id": "test",
                                "label": "test",
                                "@odata.type": "@odata.type': '#microsoft.graph.groupPolicyPresentationListBox",
                            },
                        }
                    ],
                }
            ],
            "assignments": [{"target": {"groupName": "test1"}}],
        }

        self.batch_assignment_patch = patch(
            "src.IntuneCD.update.Intune.update_groupPolicyConfiguration.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()

        self.object_assignment_patch = patch(
            "src.IntuneCD.update.Intune.update_groupPolicyConfiguration.get_object_assignment"
        )
        self.object_assignment = self.object_assignment_patch.start()

        self.update_assignment_patch = patch(
            "src.IntuneCD.update.Intune.update_groupPolicyConfiguration.update_assignment"
        )
        self.update_assignment = self.update_assignment_patch.start()

        self.post_assignment_update_patch = patch(
            "src.IntuneCD.update.Intune.update_groupPolicyConfiguration.post_assignment_update"
        )
        self.post_assignment_update = self.post_assignment_update_patch.start()

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Intune.update_groupPolicyConfiguration.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.side_effect = (
            self.mem_data_base,
            self.definition_value,
            self.presentation_value,
            self.definition_value,
        )
        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Intune.update_groupPolicyConfiguration.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update.Intune.update_groupPolicyConfiguration.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()

        self.load_file_patch = patch(
            "src.IntuneCD.update.Intune.update_groupPolicyConfiguration.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data_base

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update.Intune.update_groupPolicyConfiguration.makeapirequestDelete"
        )
        self.makeapirequestDelete = self.makeapirequestDelete_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.batch_assignment_patch.stop()
        self.object_assignment_patch.stop()
        self.update_assignment_patch.stop()
        self.post_assignment_update_patch.stop()
        self.makeapirequest_patch.stop()
        self.makeapirequestPatch_patch.stop()
        self.makeapirequestPost_patch.stop()
        self.load_file_patch.stop()
        self.makeapirequestDelete_patch.stop()

    def test_update_with_diffs_and_assignment(self):
        """The count should be 3 and the post_assignment_update and makeapirequestPatch should be called."""

        self.count = update(
            self.directory.path, self.token, assignment=True, report=False, remove=False
        )

        self.assertEqual(self.count[0].count, 3)
        self.assertEqual(self.post_assignment_update.call_count, 1)
        self.assertEqual(self.makeapirequestPost.call_count, 2)

    def test_update_with_diffs_and_assignment_report_mode(self):
        """The count should be 3 and the post_assignment_update and makeapirequestPost should be called."""

        self.count = update(
            self.directory.path,
            self.token,
            report=True,
            assignment=True,
            remove=False,
        )

        self.assertEqual(self.count[0].count, 3)
        self.assertEqual(self.post_assignment_update.call_count, 0)
        self.assertEqual(self.makeapirequestPost.call_count, 0)

    def test_update_with_diffs_and_required_presentation(self):
        """The count should be 3 and the post_assignment_update and makeapirequestPost should be called."""

        self.repo_data_base["definitionValues"][0]["presentationValues"][0][
            "presentation"
        ]["required"] = True
        self.repo_data_base["definitionValues"][0]["presentationValues"][0][
            "value"
        ] = "1"
        self.count = update(
            self.directory.path,
            self.token,
            report=False,
            assignment=False,
            remove=False,
        )

        self.assertEqual(self.count[0].count, 3)
        self.assertEqual(self.post_assignment_update.call_count, 0)
        self.assertEqual(self.makeapirequestPost.call_count, 2)

    def test_update_no_diffs_and_assignment(self):
        """The count should be 0, the post_assignment_update should be called"""

        self.repo_data_base["description"] = "test"
        self.repo_data_base["definitionValues"][0]["presentationValues"][0][
            "values"
        ] = ["test"]
        self.repo_data_base["definitionValues"][0]["enabled"] = True

        self.count = update(
            self.directory.path, self.token, assignment=True, report=False, remove=False
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.post_assignment_update.call_count, 1)
        self.assertEqual(self.makeapirequestPost.call_count, 0)

    def test_update_with_diffs_no_assignment(self):
        """The count should be 3 and the makeapirequestPost should be called."""

        self.count = update(
            self.directory.path,
            self.token,
            assignment=False,
            report=False,
            remove=False,
        )

        self.assertEqual(self.count[0].count, 3)
        self.assertEqual(self.post_assignment_update.call_count, 0)
        self.assertEqual(self.makeapirequestPost.call_count, 2)

    def test_update_with_diffs_no_assignment_no_definition_values(self):
        """The count should be 3 and the makeapirequestPost should be called."""

        self.definition_value = {"value": []}
        self.presentation_value = {"value": []}

        self.makeapirequest.side_effect = (
            self.mem_data_base,
            self.definition_value,
            self.presentation_value,
            self.definition_value,
        )

        self.count = update(
            self.directory.path,
            self.token,
            assignment=False,
            report=False,
            remove=False,
        )

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.post_assignment_update.call_count, 0)
        self.assertEqual(self.makeapirequestPost.call_count, 1)

    def test_update_config_not_found_with_assignment(self):
        """post_assignment_update should be called and makeapirequestPost should be called."""

        self.repo_data_base["displayName"] = "test1"
        self.count = update(
            self.directory.path, self.token, assignment=True, report=False, remove=False
        )

        self.assertEqual(self.post_assignment_update.call_count, 1)
        self.assertEqual(self.makeapirequestPost.call_count, 3)

    def test_update_config_not_found_and_required_presentation(self):
        """post_assignment_update should be called and makeapirequestPost should be called."""

        self.repo_data_base["displayName"] = "test1"
        self.repo_data_base["definitionValues"][0]["presentationValues"][0][
            "presentation"
        ]["required"] = True
        self.repo_data_base["definitionValues"][0]["presentationValues"][0][
            "value"
        ] = "1"
        self.count = update(
            self.directory.path,
            self.token,
            report=False,
            assignment=False,
            remove=False,
        )

        self.assertEqual(self.post_assignment_update.call_count, 1)
        self.assertEqual(self.makeapirequestPost.call_count, 2)

    def test_update_with_no_diffs_no_assignment_custom(self):
        """The count should be 3 and the makeapirequestPost should be called."""

        self.repo_data_base["policyConfigurationIngestionType"] = "custom"
        self.repo_data_base["definitionValues"][0]["definition"]["classType"] = "test"
        self.repo_data_base["definitionValues"][0]["definition"][
            "categoryPath"
        ] = "test"
        self.mem_data_base["value"][0]["policyConfigurationIngestionType"] = "custom"
        self.definition_value["value"][0]["definition"]["classType"] = "test"
        self.definition_value["value"][0]["definition"]["categoryPath"] = "test"
        self.custom_category = {
            "value": [
                {
                    "definitions": [
                        {
                            "id": "test",
                            "categoryPath": "test",
                            "classType": "test",
                            "displayName": "test",
                        }
                    ]
                }
            ]
        }

        self.makeapirequest.side_effect = [
            self.mem_data_base,
            self.definition_value,
            self.presentation_value,
            self.custom_category,
            self.definition_value,
        ]

        self.count = update(
            self.directory.path,
            self.token,
            assignment=False,
            report=False,
            remove=False,
        )

        self.assertEqual(self.count[0].count, 3)
        self.assertEqual(self.post_assignment_update.call_count, 0)
        self.assertEqual(self.makeapirequestPost.call_count, 2)

    def test_update_config_not_found_custom(self):
        """makeapirequestPost should be called."""

        self.repo_data_base["policyConfigurationIngestionType"] = "custom"
        self.repo_data_base["displayName"] = "test1"
        self.repo_data_base["definitionValues"][0]["definition"]["classType"] = "test"
        self.repo_data_base["definitionValues"][0]["definition"][
            "categoryPath"
        ] = "test"
        self.mem_data_base["value"][0]["policyConfiguraionIngestionType"] = "custom"
        self.definition_value["value"][0]["definition"]["classType"] = "test"
        self.definition_value["value"][0]["definition"]["categoryPath"] = "test"
        self.custom_category = {
            "value": [
                {
                    "definitions": [
                        {
                            "id": "test",
                            "categoryPath": "test",
                            "classType": "test",
                            "displayName": "test",
                        }
                    ]
                }
            ]
        }

        self.makeapirequest.side_effect = [
            self.mem_data_base,
            self.definition_value,
            self.presentation_value,
            self.custom_category,
            self.definition_value,
        ]

        self.makeapirequestPost.return_value = {"id": "test"}

        self.count = update(
            self.directory.path,
            self.token,
            assignment=False,
            report=False,
            remove=False,
        )

        self.assertEqual(self.makeapirequestPost.call_count, 2)

    def test_remove_config(self):
        """makeapirequestDelete should be called."""

        self.presentation_value_rm = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.groupPolicyPresentationValueList",
                    "values": ["test"],
                    "id": "test",
                    "presentation": {
                        "id": "test",
                        "label": "test",
                        "@odata.type": "@odata.type': '#microsoft.graph.groupPolicyPresentationListBox",
                    },
                }
            ]
        }
        self.definition_value_rm = {
            "value": [
                {
                    "enabled": True,
                    "configurationType": "Policy",
                    "id": "test",
                    "definition": {
                        "id": "test",
                        "displayName": "test",
                    },
                    "presentationValues": [],
                }
            ]
        }
        self.mem_data_base_rm = {
            "value": [
                {
                    "id": "test",
                    "displayName": "test2",
                    "description": "test",
                    "definitionValues": [],
                    "policyConfigurationIngestionType": "BuiltIn",
                    "assignments": [{"target": {"groupName": "test"}}],
                }
            ]
        }

        self.makeapirequest.side_effect = (
            self.mem_data_base_rm,
            self.definition_value_rm,
            self.presentation_value_rm,
            self.definition_value_rm,
        )

        self.update = update(self.directory.path, self.token, report=False, remove=True)

        self.assertEqual(self.makeapirequestDelete.call_count, 1)


if __name__ == "__main__":
    unittest.main()
