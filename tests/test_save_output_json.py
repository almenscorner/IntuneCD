#!/usr/bin/env python3

"""
This module tests the save_output function with a JSON file.
"""

import unittest
import json

from testfixtures import TempDirectory
from unittest.mock import patch
from src.IntuneCD.save_output import save_output

directory = TempDirectory()
directory.create()


class TestSaveOutputJson(unittest.TestCase):
    """Test class for save_output."""

    def setUp(self):
        self.path = f"{directory.path}/"
        self.output = "json"
        self.fname = "file_name"
        self.data = {"test_content": "Hello World"}
        self.save = save_output(self.output, self.path, self.fname, self.data)

        with open(self.path + self.fname + ".json", 'r') as f:
            self.json = json.load(f)

    def tearDown(self):
        directory.cleanup()

    @patch("json.load")
    @patch("src.IntuneCDBeta.save_output")
    def test_file_content(self, mock_load, mock_json):
        """The file created by the processor should have the expected contents."""
        mock_json.load.return_value = {
            'test_content': 'Hello World'
        }
        self.assertEqual(self.json['test_content'], mock_json.load.return_value['test_content'])
