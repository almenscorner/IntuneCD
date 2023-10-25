#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module tests the graph_batch module.
"""

import unittest
from unittest.mock import patch

from src.IntuneCD.intunecdlib.graph_batch import (
    batch_assignment,
    batch_intents,
    batch_request,
    get_object_assignment,
    get_object_details,
)


class TestGraphBatch(unittest.TestCase):
    """Test class for graph_batch."""

    def setUp(self):
        self.token = "token"
        self.batch_request_data = ["1", "2", "3"]
        self.batch_assignment_data = {"value": [{"id": "0"}]}
        self.batch_intents_data = {
            "value": [
                {
                    "id": "0",
                    "templateId": "0",
                    "displayName": "test",
                    "description": "",
                    "roleScopeTagIds": ["0"],
                }
            ]
        }
        self.responses = [
            {
                "value": [
                    {
                        "target": {
                            "groupId": "0",
                            "deviceAndAppManagementAssignmentFilterId": "0",
                        }
                    }
                ]
            }
        ]
        self.group_responses = [
            {
                "displayName": "test",
                "id": "0",
                "groupTypes": ["DynamicMembership"],
                "membershipRule": "test",
            }
        ]
        self.filter_responses = [{"displayName": "test", "id": "0"}]
        self.category_responses = [
            {
                "@odata.context": "https://graph.microsoft.com/beta/$metadata#deviceManagement/templates('0')/categories",
                "value": [{"id": "0", "displayName": "test"}],
            }
        ]
        self.settings_responses = [
            {
                "@odata.context": "https://graph.microsoft.com/beta/$metadata#deviceManagement/intents('0')/categories('0')/settings",
                "value": [
                    {
                        "@odata.type": "#microsoft.graph.deviceManagementBooleanSettingInstance",
                        "id": "0",
                        "definitionId": "Protection",
                        "valueJson": "null",
                        "value": None,
                    }
                ],
            }
        ]

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.intunecdlib.graph_batch.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()

        self.get_object_details_patch = patch(
            "src.IntuneCD.intunecdlib.graph_batch.get_object_details"
        )
        self.get_object_details = self.get_object_details_patch.start()

        self.get_object_assignment_patch = patch(
            "src.IntuneCD.intunecdlib.graph_batch.get_object_assignment"
        )
        self.get_object_assignment = self.get_object_assignment_patch.start()

        self.batch_intents_patch = patch(
            "src.IntuneCD.intunecdlib.graph_batch.batch_intents"
        )
        self.batch_intents = self.batch_intents_patch.start()

        self.batch_assignment_patch = patch(
            "src.IntuneCD.intunecdlib.graph_batch.batch_assignment"
        )
        self.batch_assignment = self.batch_assignment_patch.start()

        self.batch_request_patch = patch(
            "src.IntuneCD.intunecdlib.graph_batch.batch_request"
        )
        self.batch_request = self.batch_request_patch.start()
        self.batch_request.side_effect = (
            self.responses,
            self.group_responses,
            self.filter_responses,
        )

    def tearDown(self):
        self.makeapirequestPost.stop()
        self.get_object_details.stop()
        self.get_object_assignment.stop()
        self.batch_intents.stop()
        self.batch_assignment.stop()
        self.batch_request.stop()

    def test_batch_request(self):
        """The batch request function should return the expected result."""

        self.expected_result = [
            {"odata.count": 1, "value": [{"id": "0", "displayName": "test"}]}
        ]
        self.makeapirequestPost.return_value = {
            "responses": [
                {
                    "id": "5",
                    "status": 200,
                    "body": {
                        "odata.count": 1,
                        "value": [{"id": "0", "displayName": "test"}],
                    },
                }
            ]
        }
        self.result = batch_request(self.batch_request_data, "test", "test", self.token)

        self.assertEqual(self.result, self.expected_result)

    def test_batch_assignment(self):
        """The batch assignment function should return the expected result."""

        self.expected_result = [
            {
                "value": [
                    {
                        "target": {
                            "deviceAndAppManagementAssignmentFilterId": "test",
                            "groupId": "0",
                            "groupName": "test",
                            "groupType": "DynamicMembership",
                            "membershipRule": "test",
                        }
                    }
                ]
            }
        ]
        self.result = batch_assignment(
            self.batch_assignment_data, "test", "test", self.token
        )

        self.assertEqual(self.result, self.expected_result)

    def test_batch_assignment_expand_assignments(self):
        """The batch assignment function should return the expected result."""

        self.responses = [
            {
                "assignments@odata.context": "test",
                "assignments": [
                    {
                        "target": {
                            "groupId": "0",
                            "deviceAndAppManagementAssignmentFilterId": "0",
                        }
                    }
                ],
            }
        ]

        self.batch_request.side_effect = (
            self.responses,
            self.group_responses,
            self.filter_responses,
        )

        self.expected_result = [
            {
                "@odata.context": "test",
                "value": [
                    {
                        "target": {
                            "deviceAndAppManagementAssignmentFilterId": "test",
                            "groupId": "0",
                            "groupName": "test",
                            "groupType": "DynamicMembership",
                            "membershipRule": "test",
                        }
                    }
                ],
            }
        ]
        self.result = batch_assignment(
            self.batch_assignment_data, "test", "?$expand=assignments", self.token
        )

        self.assertEqual(self.result, self.expected_result)

    def test_batch_assignment_appProtection_mdmWindowsInformationProtectionPolicy(self):
        """The batch assignment function should return the expected result for the platform."""

        self.batch_assignment_data = {
            "value": [
                {
                    "id": "0",
                    "@odata.type": "#microsoft.graph.mdmWindowsInformationProtectionPolicy",
                }
            ]
        }

        self.expected_result = [
            {
                "value": [
                    {
                        "target": {
                            "deviceAndAppManagementAssignmentFilterId": "test",
                            "groupId": "0",
                            "groupName": "test",
                            "groupType": "DynamicMembership",
                            "membershipRule": "test",
                        }
                    }
                ]
            }
        ]
        self.result = batch_assignment(
            self.batch_assignment_data, "test", "test", self.token, app_protection=True
        )

        self.assertEqual(self.result, self.expected_result)

    def test_batch_assignment_appProtection_windowsInformationProtectionPolicy(self):
        """The batch assignment function should return the expected result for the platform."""

        self.batch_assignment_data = {
            "value": [
                {
                    "id": "0",
                    "@odata.type": "#microsoft.graph.windowsInformationProtectionPolicy",
                }
            ]
        }

        self.expected_result = [
            {
                "value": [
                    {
                        "target": {
                            "deviceAndAppManagementAssignmentFilterId": "test",
                            "groupId": "0",
                            "groupName": "test",
                            "groupType": "DynamicMembership",
                            "membershipRule": "test",
                        }
                    }
                ]
            }
        ]
        self.result = batch_assignment(
            self.batch_assignment_data, "test", "test", self.token, app_protection=True
        )

        self.assertEqual(self.result, self.expected_result)

    def test_batch_assignment_appProtection_iosManagedAppProtection(self):
        """The batch assignment function should return the expected result for the platform."""

        self.batch_assignment_data = {
            "value": [
                {"id": "0", "@odata.type": "#microsoft.graph.iosManagedAppProtection"}
            ]
        }

        self.expected_result = [
            {
                "value": [
                    {
                        "target": {
                            "deviceAndAppManagementAssignmentFilterId": "test",
                            "groupId": "0",
                            "groupName": "test",
                            "groupType": "DynamicMembership",
                            "membershipRule": "test",
                        }
                    }
                ]
            }
        ]
        self.result = batch_assignment(
            self.batch_assignment_data, "test", "test", self.token, app_protection=True
        )

        self.assertEqual(self.result, self.expected_result)

    def test_batch_intents(self):
        """The batch intents function should return the expected result."""

        self.batch_request.side_effect = (
            self.category_responses,
            self.settings_responses,
        )
        self.expected_result = {
            "value": [
                {
                    "description": "",
                    "displayName": "test",
                    "id": "0",
                    "roleScopeTagIds": ["0"],
                    "settingsDelta": [
                        {
                            "@odata.type": "#microsoft.graph.deviceManagementBooleanSettingInstance",
                            "definitionId": "Protection",
                            "id": "0",
                            "value": None,
                            "valueJson": "null",
                        }
                    ],
                    "templateId": "0",
                }
            ]
        }
        self.result = batch_intents(self.batch_intents_data, self.token)

        self.assertEqual(self.result, self.expected_result)

    def test_get_object_assignment(self):
        """The get object assignment function should return the expected result."""

        self.id = "0"
        self.response = [
            {
                "@odata.context": "https://graph.microsoft.com/beta/$metadata#deviceAppManagement/mobileAppConfigurations('0')/assignments",
                "value": [{"id": "0", "target": {"groupId": "0", "groupName": "test"}}],
            }
        ]
        self.expected_result = [{"target": {"groupName": "test"}}]

        self.result = get_object_assignment(self.id, self.response)

        self.assertEqual(self.result, self.expected_result)

    def test_get_object_details(self):
        """The get object details function should return the expected result."""

        self.id = "0"
        self.response = [
            {
                "@odata.context": "https://graph.microsoft.com/beta/$metadata#deviceAppManagement/mobileAppConfigurations('0')",
                "value": [
                    {
                        "id": "0",
                        "displayName": "test",
                        "description": "",
                        "templateId": "0",
                        "roleScopeTagIds": ["0"],
                        "settingsDelta": [
                            {
                                "@odata.type": "#microsoft.graph.deviceManagementBooleanSettingInstance",
                                "definitionId": "Protection",
                                "id": "0",
                                "value": None,
                                "valueJson": "null",
                            }
                        ],
                    }
                ],
            }
        ]
        self.expected_result = [
            {
                "description": "",
                "displayName": "test",
                "id": "0",
                "roleScopeTagIds": ["0"],
                "settingsDelta": [
                    {
                        "@odata.type": "#microsoft.graph.deviceManagementBooleanSettingInstance",
                        "definitionId": "Protection",
                        "id": "0",
                        "value": None,
                        "valueJson": "null",
                    }
                ],
                "templateId": "0",
            }
        ]

        self.result = get_object_details(self.id, self.response)

        self.assertEqual(self.result, self.expected_result)


if __name__ == "__main__":
    unittest.main()
