#!/usr/bin/env python3

"""
This module tests the save_output function with a YAML file.
"""

import unittest
import yaml
import json

from testfixtures import TempDirectory
from unittest.mock import patch
from src.IntuneCD.save_output import save_output

directory = TempDirectory()
directory.create()


class TestSaveOutputYaml(unittest.TestCase):
    """Test class for save_output."""

    def setUp(self):
        self.path = f"{directory.path}/"
        self.output = "yaml"
        self.fname = "file_name"
        self.data = {"test_content": "Hello World"}
        self.save = save_output(self.output, self.path, self.fname, self.data)

        with open(self.path + self.fname + ".yaml", 'r') as f:
            data = json.dumps(yaml.safe_load(f))
            self.yaml = json.loads(data)

    def tearDown(self):
        directory.cleanup()

    @patch("src.IntuneCDBeta.save_output")
    @patch("json.load")
    def test_file_content(self, mock_load, mock_json):
        """The file created by the processor should have the expected contents."""
        mock_json.load.return_value = {
            'test_content': 'Hello World'
        }
        self.assertEqual(
            self.yaml['test_content'],
            mock_json.load.return_value['test_content'])
