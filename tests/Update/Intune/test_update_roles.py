# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from testfixtures import TempDirectory

from src.IntuneCD.update.Intune.update_roles import update


class TestUpdaterole(unittest.TestCase):
    """Test class for update_role."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Roles")
        self.directory.write("Roles/test.json", '{"test": "test"}', encoding="utf-8")
        self.directory.write("Roles/test.txt", '{"test": "test"}', encoding="utf-8")
        self.token = "token"
        self.mem_data = {
            "value": [
                {
                    "@odata.type": "#microsoft.graph.deviceAndAppManagementRoleDefinition",
                    "displayName": "test",
                    "description": "",
                    "id": "0",
                    "isBuiltInRoleDefinition": False,
                    "isBuiltIn": False,
                    "roleScopeTagIds": ["0"],
                    "permissions": [],
                    "rolePermissions": [
                        {
                            "actions": [],
                            "resourceActions": [
                                {
                                    "allowedResourceActions": [
                                        "Microsoft.Intune_DeviceConfigurations_Read"
                                    ],
                                    "notAllowedResourceActions": [],
                                }
                            ],
                        }
                    ],
                }
            ]
        }
        self.repo_data = {
            "@odata.type": "#microsoft.graph.deviceAndAppManagementRoleDefinition",
            "displayName": "test",
            "description": "",
            "isBuiltInRoleDefinition": False,
            "isBuiltIn": False,
            "rolePermissions": [
                {
                    "resourceActions": [
                        {
                            "allowedResourceActions": [
                                "Microsoft.Intune_DeviceConfigurations_Read"
                            ],
                            "notAllowedResourceActions": [],
                        }
                    ]
                }
            ],
            "roleAssignments": [
                {
                    "displayName": "test",
                    "description": "",
                    "scopeMembers": ["admin"],
                    "scopeType": "resourceScope",
                    "members": ["test"],
                }
            ],
        }

        self.makeapirequest_patch = patch(
            "src.IntuneCD.update.Intune.update_roles.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = self.mem_data

        self.load_file_patch = patch(
            "src.IntuneCD.update.Intune.update_roles.load_file"
        )
        self.load_file = self.load_file_patch.start()
        self.load_file.return_value = self.repo_data

        self.makeapirequestPatch_patch = patch(
            "src.IntuneCD.update.Intune.update_roles.makeapirequestPatch"
        )
        self.makeapirequestPatch = self.makeapirequestPatch_patch.start()

        self.makeapirequestPost_patch = patch(
            "src.IntuneCD.update.Intune.update_roles.makeapirequestPost"
        )
        self.makeapirequestPost = self.makeapirequestPost_patch.start()
        self.makeapirequestPost.return_value = {"id": "0"}

        self.makeapirequestDelete_patch = patch(
            "src.IntuneCD.update.Intune.update_roles.makeapirequestDelete"
        )
        self.makeapirequestDelete = self.makeapirequestDelete_patch.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest_patch.stop()
        self.load_file_patch.stop()
        self.makeapirequestPatch_patch.stop()
        self.makeapirequestPost_patch.stop()
        self.makeapirequestDelete_patch.stop()

    def test_update_with_diffs(self):
        """The count should be 1 and makeapirequestPatch should be called."""
        self.repo_data["description"] = "test"

        self.count = update(self.directory.path, self.token, report=False, remove=False)

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)

    def test_update_with_multiple_diffs(self):
        """The count should be 1 and makeapirequestPatch should be called."""

        self.repo_data["description"] = "test"
        self.repo_data["rolePermissions"][0]["resourceActions"][0][
            "allowedResourceActions"
        ].append("test")

        self.count = update(self.directory.path, self.token, report=False, remove=False)

        self.assertEqual(self.count[0].count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)
        self.assertEqual(self.makeapirequestPatch.call_count, 1)

    def test_update_with_no_diffs(self):
        """The count should be 0 and makeapirequestPatch should not be called."""

        self.count = update(self.directory.path, self.token, report=False, remove=False)

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)

    def test_update_config_not_found(self):
        """The count should be 0 and makeapirequestPost should be called."""

        self.mem_data["value"][0]["displayName"] = "test1"
        self.count = update(self.directory.path, self.token, report=False, remove=False)

        self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestPost.call_count, 1)

    def test_update_config_not_found_remove(self):
        """The count should be 0 and makeapirequestPost should be called."""

        self.mem_data["value"].append(
            {
                "displayName": "test2",
                "id": "0",
            }
        )
        self.count = update(self.directory.path, self.token, report=False, remove=True)

        # self.assertEqual(self.count, [])
        self.assertEqual(self.makeapirequestDelete.call_count, 1)

    def test_update_scope_tags(self):
        """The count should be 1 and the post_assignment_update and makeapirequestPatch should be called."""

        self.count = update(
            self.directory.path,
            self.token,
            remove=False,
            report=False,
            scope_tags=["test"],
        )

        self.assertEqual(self.count[0].count, 0)
        self.assertEqual(self.makeapirequestPatch.call_count, 0)


if __name__ == "__main__":
    unittest.main()
