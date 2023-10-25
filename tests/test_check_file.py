#!/usr/bin/env/python3
# -*- coding: utf-8 -*-

"""
This module tests the check_file function.
"""

import unittest

from testfixtures import TempDirectory

from src.IntuneCD.intunecdlib.check_file import check_file


class TestCheckFile(unittest.TestCase):
    """Test class for check_file."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.yaml = "file_name.yaml"
        self.json = "file_name.json"
        self.md = "file_name.md"
        self.DS_Store = ".DS_Store"
        self.d = self.directory.makedir("fake_path")

        self.yaml_file = self.directory.write(self.yaml, "yaml", encoding="utf-8")
        self.json_file = self.directory.write(
            self.json, '{"data": "fake_data"}', encoding="utf-8"
        )
        self.md_file = self.directory.write(self.md, "md", encoding="utf-8")
        self.DS_Store_file = self.directory.write(
            self.DS_Store, "DS_Store", encoding="utf-8"
        )

    def tearDown(self):
        self.directory.cleanup()

    def test_check_yaml_file(self):
        """Should return True if the file is a yaml file."""
        self.check = check_file(self.directory.path, self.yaml)
        self.assertTrue(self.check)

    def test_check_json_file(self):
        """Should return True if the file is a json file."""
        self.check = check_file(self.directory.path, self.json)
        self.assertTrue(self.check)

    def test_check_md_file(self):
        """Should return False if the file is a md file."""
        self.check = check_file(self.directory.path, self.md)
        self.assertFalse(self.check)

    def test_check_DS_Store_file(self):
        """Should return False if the file is a DS_Store file."""
        self.check = check_file(self.directory.path, self.DS_Store)
        self.assertFalse(self.check)

    def test_check_dir(self):
        """Should return False if the file is a directory."""
        self.check = check_file(self.directory.path, self.d)
        self.assertFalse(self.check)


if __name__ == "__main__":
    unittest.main()
