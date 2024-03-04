#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module tests the process_scope_tags function.
"""

import unittest
from unittest.mock import patch

from src.IntuneCD.intunecdlib.process_scope_tags import get_scope_tags


class TestGetScopeTags(unittest.TestCase):
    """Test class for get_scope_tags."""

    def setUp(self):
        self.data = {"id": "1", "displayName": "Test"}
        self.token = {"access_token": "test"}

        self.get_scope_tags_patch = patch(
            "src.IntuneCD.intunecdlib.process_scope_tags.get_scope_tags"
        )
        self.get_scope_tags = self.get_scope_tags_patch.start()
        self.get_scope_tags.return_value = [self.data]

        self.makeapirequest_patch = patch(
            "src.IntuneCD.intunecdlib.process_scope_tags.makeapirequest"
        )
        self.makeapirequest = self.makeapirequest_patch.start()
        self.makeapirequest.return_value = {"value": [self.data]}

    def tearDown(self):
        self.get_scope_tags_patch.stop()

    def test_get_scope_tags(self):
        """The odata type should match the expected value."""
        self.result = get_scope_tags(self.token)

        self.assertEqual(self.result, [self.data])


if __name__ == "__main__":
    unittest.main()
