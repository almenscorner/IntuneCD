# -*- coding: utf-8 -*-
import ast
import json
import os
import unittest

from testfixtures import TempDirectory

from src.IntuneCD.intunecdlib.assignment_report import get_group_report


class TestGetGroupReport(unittest.TestCase):
    """Test class for get_group_report."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.directory.makedir("Device Configurations")
        self.directory.makedir("Compliance Policies/Policies")
        self.directory.write(
            "Device Configurations/test.json",
            '{"displayName": "testconfig","assignments": [{"target": {"groupName": "test1","groupType": "DynamicMembership","membershipRule": "test"}}]}',
            encoding="utf-8",
        )
        self.directory.write(
            "Compliance Policies/Policies/test.json",
            '{"@odata.type": "#type.super.duper","displayName": "testconfig","assignments": [{"intent": "force","target": {"groupName": "test1","groupType": "DynamicMembership","membershipRule": "test"}}]}',
            encoding="utf-8",
        )

    def tearDown(self):
        """Remove the test folder and all its contents"""
        # Remove the test folder and all its contents
        self.directory.cleanup()

    def test_get_group_report(self):
        """The folder should be created and the file should have the expected contents"""

        # Test that the function returns the expected output for the sample file
        expected_output = [
            {
                "assignedTo": {
                    "Compliance Policies": [
                        {"name": "testconfig", "type": "duper", "intent": "force"}
                    ],
                    "Device Configurations": [
                        {"name": "testconfig", "type": "", "intent": ""}
                    ],
                },
                "groupName": "test1",
                "groupType": "DynamicMembership",
                "membershipRule": "test",
            }
        ]
        get_group_report(self.directory.path, "json")
        with open(
            os.path.join(self.directory.path, "Assignment Report", "report.json"),
            "r",
            encoding="utf-8",
        ) as f:
            actual_output = ast.literal_eval(f.read())
        self.assertEqual(actual_output, expected_output)

    def test_get_group_report_no_files(self):
        """The folder should not be created and the file should not be created"""

        # Test that the function returns an empty list when no files are found
        with open(
            os.path.join(self.directory.path, "Device Configurations", "test.json"),
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)
        with open(
            os.path.join(self.directory.path, "Device Configurations", "test.json"),
            "w",
            encoding="utf-8",
        ) as f:
            data.pop("assignments")
            json.dump(data, f)
        with open(
            os.path.join(
                self.directory.path, "Compliance Policies/Policies", "test.json"
            ),
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)
        with open(
            os.path.join(
                self.directory.path, "Compliance Policies/Policies", "test.json"
            ),
            "w",
            encoding="utf-8",
        ) as f:
            data.pop("assignments")
            json.dump(data, f)

        get_group_report(self.directory.path, "json")
        path_exists = os.path.exists(
            os.path.join(self.directory.path, "Assignment Report")
        )
        self.assertEqual(path_exists, False)
