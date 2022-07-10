#!/usr/bin/env python3

"""
This module tests the match function.
"""

import unittest

from src.IntuneCD.backup_applications import match


class TestMatch(unittest.TestCase):
    """Test class for match."""

    def test_match(self):
        """The odata type should match the expected value."""
        self.app = {'@odata.type': '#microsoft.graph.macOsVppApp'}

        if match('macos', str(self.app['@odata.type']).lower()) is True:
            self.platform = 'macOS'

        self.assertEqual(self.platform, "macOS")
