#!/usr/bin/env python3

"""
This module tests the clean_filename function.
"""

import unittest

from src.IntuneCD.clean_filename import clean_filename


class TestCleanFilename(unittest.TestCase):
    """Test class for clean_filename."""

    def test_clean_filename(self):
        """The filename should be returned with the characters replaced."""
        self.filename = "test|file:name"

        result = clean_filename(self.filename)

        self.assertEqual(result, "test_file_name")
