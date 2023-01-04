#!/usr/bin/env python3

"""
This module tests the get_diff_output function.
"""

import unittest

from src.IntuneCD.diff_summary import DiffSummary
from datetime import datetime

now = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class TestGetDiffOutput(unittest.TestCase):
    """Test class for get_diff_output."""

    def test_get_diff_output_single(self):
        """Should return a list of dicts with the setting, new value and old value."""
        diff = {"root['cameraBlocked']": {"new_value": True, "old_value": False, "change_date": now}}

        self.output = DiffSummary(data=diff, name="Test", type="configurationProfile")

        self.assertEqual(
            self.output.diffs,
            [{"new_val": "True", "old_val": "False", "setting": "cameraBlocked", "change_date": now}],
        )

    def test_get_diff_output_multiple(self):
        """Should return a list of dicts with the settings, new values and old values."""
        diff = {
            "root['cameraBlocked']": {"new_value": True, "old_value": False, "change_date": now},
            "root['cameraBlocked2']": {"new_value": True, "old_value": False, "change_date": now},
        }

        self.output = DiffSummary(data=diff, name="Test", type="configurationProfile")

        self.assertEqual(
            self.output.diffs,
            [
                {"new_val": "True", "old_val": "False", "setting": "cameraBlocked", "change_date": now},
                {"new_val": "True", "old_val": "False", "setting": "cameraBlocked2", "change_date": now},
            ],
        )


if __name__ == "__main__":
    unittest.main()
