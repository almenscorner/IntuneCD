#!/usr/bin/env/python3
# -*- coding: utf-8 -*-

"""
This module tests the check_file function.
"""

import unittest

from src.IntuneCD.intunecdlib.check_prefix import check_prefix_match


class TestCheckFile(unittest.TestCase):
    """Test class for check_file."""

    def test_prefix_true(self):
        """Should return True if the prefix is correct."""
        self.prefix = check_prefix_match("test1 - platform - configtype", "test1")
        self.assertTrue(self.prefix)

    def test_prefix_false(self):
        """Should return False if the prefix is incorrect."""
        self.prefix = check_prefix_match("test1 - platform - configtype", "test2")
        self.assertFalse(self.prefix)


if __name__ == "__main__":
    unittest.main()
