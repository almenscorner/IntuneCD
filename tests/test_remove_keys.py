#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from src.IntuneCD.intunecdlib.remove_keys import remove_keys


class TestRemoveKeys(unittest.TestCase):
    """Test class for remove_keys."""

    def test_remove_keys(self):
        """The dict should be returned with the keys removed."""
        self.dict = {
            "id": "1",
            "isGlobalScript": True,
            "lastModifiedDateTime": "2022-07-06",
            "awesome_key": "awesome_value",
        }

        self.dict = remove_keys(self.dict)

        self.assertEqual(self.dict, {"awesome_key": "awesome_value"})


if __name__ == "__main__":
    unittest.main()
