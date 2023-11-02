#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module tests the match function.
"""

import unittest

from src.IntuneCD.backup.Intune.backup_applications import match


class TestMatch(unittest.TestCase):
    """Test class for match."""

    def test_match_macOS(self):
        """The odata type should match the expected value."""
        self.app = {"@odata.type": "#microsoft.graph.macOsVppApp"}

        self.result = ("macos", str(self.app["@odata.type"]).lower())

        self.assertTrue(self.result)

    def test_match_ios(self):
        """The odata type should match the expected value."""
        self.app = {"@odata.type": "#microsoft.graph.iosStoreApp"}

        self.result = ("ios", str(self.app["@odata.type"]).lower())

        self.assertTrue(self.result)

    def test_match_windows(self):
        """The odata type should match the expected value."""
        self.app = {"@odata.type": "#microsoft.graph.win32LobApp"}

        self.result = match("win32", str(self.app["@odata.type"]).lower())

        self.assertTrue(self.result)

    def test_match_android(self):
        """The odata type should match the expected value."""
        self.app = {"@odata.type": "#microsoft.graph.androidStoreApp"}

        self.result = match("android", str(self.app["@odata.type"]).lower())

        self.assertTrue(self.result)

    def test_match_unknown(self):
        """Unkown odata type should return false."""
        self.app = {"@odata.type": "#microsoft.graph.unknown"}

        self.result = match("iOS", str(self.app["@odata.type"]).lower())

        self.assertFalse(self.result)


if __name__ == "__main__":
    unittest.main()
