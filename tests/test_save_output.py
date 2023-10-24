#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module tests the save_output function with a JSON file.
"""

import json
import unittest
from unittest.mock import patch

import yaml
from testfixtures import TempDirectory

from src.IntuneCD.intunecdlib.save_output import save_output


@patch("src.IntuneCD.intunecdlib.save_output")
class TestSaveOutput(unittest.TestCase):
    """Test class for save_output."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.path = f"{self.directory.path}/"
        self.fname = "file_name"
        self.data = {"test_content": "Hello World"}
        self.expected_data = {"test_content": "Hello World"}

    def tearDown(self):
        self.directory.cleanup()

    def test_save_output_json(self, _):
        """The file created by the function should have the expected contents."""
        save_output("json", self.path, self.fname, self.data)

        with open(self.path + self.fname + ".json", "r", encoding="utf-8") as f:
            self.json = json.load(f)

        self.assertEqual(self.json["test_content"], self.expected_data["test_content"])

    def test_save_output_yaml(self, _):
        """The file created by the function should have the expected contents."""
        save_output("yaml", self.path, self.fname, self.data)

        with open(self.path + self.fname + ".yaml", "r", encoding="utf-8") as f:
            data = json.dumps(yaml.safe_load(f))
            self.yaml = json.loads(data)

        self.assertEqual(self.yaml["test_content"], self.expected_data["test_content"])

    def test_save_output_invalid_format(self, _):
        """The function should raise an error if the format is invalid."""
        with self.assertRaises(ValueError):
            save_output("invalid", self.path, self.fname, self.data)


if __name__ == "__main__":
    unittest.main()
