#!/usr/bin/env/python3

"""
This module tests the load_file function.
"""

import unittest

from testfixtures import TempDirectory
from src.IntuneCD.load_file import load_file

directory = TempDirectory()
directory.create()


class TestLoadFile(unittest.TestCase):
    """Test class for load_file."""

    def setUp(self):
        self.yaml_name = "file_name.yaml"
        self.json_name = "file_name.json"
        self.yaml_file = directory.write(
            self.yaml_name,
            "yaml",
            encoding="utf-8")
        self.json_file = directory.write(
            self.json_name,
            '{"data": "fake_data"}',
            encoding="utf-8")

        with open(self.yaml_file) as f:
            self.yaml = load_file(self.yaml_name, f)

        with open(self.json_file) as f:
            self.json = load_file(self.json_name, f)

    def tearDown(self):
        directory.cleanup()

    def test_load_file(self):
        """Only yaml and json files should be returned."""
        self.assertIsNotNone(self.yaml)
        self.assertIsNotNone(self.json)
