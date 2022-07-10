#!/usr/bin/env/python3

"""
This module tests the check_file function.
"""

import unittest

from testfixtures import TempDirectory
from src.IntuneCD.check_file import check_file

directory = TempDirectory()
directory.create()


class TestCheckFile(unittest.TestCase):
    """Test class for check_file."""

    def setUp(self):
        self.yaml = "file_name.yaml"
        self.json = "file_name.json"
        self.md = "file_name.md"
        self.DS_Store = ".DS_Store"
        self.d = directory.makedir("fake_path")

        self.yaml_file = directory.write(self.yaml, "yaml", encoding="utf-8")
        self.json_file = directory.write(
            self.json, '{"data": "fake_data"}', encoding="utf-8")
        self.md_file = directory.write(self.md, "md", encoding="utf-8")
        self.DS_Store_file = directory.write(
            self.DS_Store, "DS_Store", encoding="utf-8")

        self.yaml_check = check_file(directory.path, self.yaml)
        self.json = check_file(directory.path, self.json)
        self.md = check_file(directory.path, self.md)
        self.DS_Store = check_file(directory.path, self.DS_Store)
        self.dir = check_file(directory.path, self.d)

    def tearDown(self):
        directory.cleanup()

    def test_check_file(self):
        """Only yaml and json files should be returned."""
        self.assertTrue(self.yaml_check)
        self.assertTrue(self.json)
        self.assertFalse(self.md)
        self.assertFalse(self.DS_Store)
        self.assertFalse(self.dir)
