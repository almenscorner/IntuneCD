#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module tests the clean_filename function.
"""

import unittest

from src.IntuneCD.intunecdlib.clean_filename import clean_filename


class TestCleanFilename(unittest.TestCase):
    """Test class for clean_filename."""

    def test_clean_filename_string(self):
        """The filename should be returned with the characters replaced."""
        self.filename = "test|file:name"

        result = clean_filename(self.filename)

        self.assertEqual(result, "test_file_name")

    def test_clean_filename_list(self):
        """The filename should be returned with the characters replaced."""
        self.filename = ["test|file:name", "test|file:name"]

        result = clean_filename(self.filename)

        self.assertEqual(result, "['test_file_name', 'test_file_name']")


if __name__ == "__main__":
    unittest.main()
