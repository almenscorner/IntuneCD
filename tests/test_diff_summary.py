#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module tests the get_diff_output function.
"""

import unittest
from unittest.mock import patch

from src.IntuneCD.intunecdlib.diff_summary import DiffSummary


@patch(
    "src.IntuneCD.intunecdlib.diff_summary.datetime", return_value="2021-01-01 00:00:00"
)
class TestGetDiffOutput(unittest.TestCase):
    """Test class for get_diff_output."""

    def test_get_diff_output_single(self, mock_datetime):
        """Should return a list of dicts with the setting, new value and old value."""
        diff = {"root['cameraBlocked']": {"new_value": True, "old_value": False}}

        self.output = DiffSummary(data=diff, name="Test", type="configurationProfile")

        self.assertEqual(
            self.output.diffs,
            [
                {
                    "new_val": "True",
                    "old_val": "False",
                    "setting": "cameraBlocked",
                    "change_date": str(
                        mock_datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                }
            ],
        )

    def test_get_diff_output_multiple(self, mock_datetime):
        """Should return a list of dicts with the settings, new values and old values."""
        diff = {
            "root['cameraBlocked']": {"new_value": True, "old_value": False},
            "root['cameraBlocked2']": {"new_value": True, "old_value": False},
        }

        self.output = DiffSummary(data=diff, name="Test", type="configurationProfile")

        self.assertEqual(
            self.output.diffs,
            [
                {
                    "new_val": "True",
                    "old_val": "False",
                    "setting": "cameraBlocked",
                    "change_date": str(
                        mock_datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                },
                {
                    "new_val": "True",
                    "old_val": "False",
                    "setting": "cameraBlocked2",
                    "change_date": str(
                        mock_datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
