#!/usr/bin/env python3

"""
This module tests the get_diff_output function.
"""

import unittest

from src.IntuneCD.get_diff_output import get_diff_output


class TestGetDiffOutput(unittest.TestCase):
    """Test class for get_diff_output."""

    def test_get_diff_output(self):
        """Should return a string with the setting, new value and old value."""
        diff = {
            "root['cameraBlocked']": {
                'new_value': True,
                'old_value': False}}

        self.output = get_diff_output(diff)

        self.assertEqual(
            self.output,
            "Setting: 'cameraBlocked', New Value: True, Old Value: False")
