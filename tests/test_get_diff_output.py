#!/usr/bin/env python3

"""
This module tests the get_diff_output function.
"""

import unittest

from src.IntuneCD.get_diff_output import get_diff_output


class TestGetDiffOutput(unittest.TestCase):
    """Test class for get_diff_output."""

    def test_get_diff_output_single(self):
        """Should return a list with the setting, new value and old value."""
        diff = {
            "root['cameraBlocked']": {
                'new_value': True,
                'old_value': False}}

        self.output = get_diff_output(diff)

        self.assertEqual(
            self.output,
            ["Setting: 'cameraBlocked', New Value: True, Old Value: False"])

    def test_get_diff_output_multiple(self):
        """Should return a list with the settings, new values and old values."""
        diff = {
            "root['cameraBlocked']": {
                'new_value': True,
                'old_value': False},
            "root['cameraBlocked2']": {
                'new_value': True,
                'old_value': False}}

        self.output = get_diff_output(diff)

        self.assertEqual(
            self.output,
            ["Setting: 'cameraBlocked', New Value: True, Old Value: False",
             "Setting: 'cameraBlocked2', New Value: True, Old Value: False"])


if __name__ == '__main__':
    unittest.main()
