# -*- coding: utf-8 -*-
import tempfile
import unittest
from unittest.mock import patch

from src.IntuneCD.update.Intune.DeviceConfigurations import (
    DeviceConfigurationsUpdateModule,
)


def _oma(uri: str, value: str) -> dict:
    return {
        "@odata.type": "#microsoft.graph.omaSettingString",
        "displayName": uri,
        "description": None,
        "omaUri": uri,
        "isEncrypted": False,
        "secretReferenceValueId": None,
        "value": value,
    }


class TestDeviceConfigurationsCustomWindows(unittest.TestCase):
    """Tests for patching Windows custom (OMA-URI) profiles."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.module = DeviceConfigurationsUpdateModule(path=self.temp_dir.name)
        self.module.downstream_id = "profile-id"
        self.module.name = "Custom profile"
        self.module.config_type = "OMA-URI"
        self.module.notify = False

    def tearDown(self):
        self.temp_dir.cleanup()

    def _patched(self, intune_values: list, repo_values: list) -> bool:
        """Run the OMA comparison and return whether the profile was patched."""
        intune_data = {
            "omaSettings": [_oma(f"./A/{i}", v) for i, v in enumerate(intune_values)]
        }
        repo_data = {
            "omaSettings": [_oma(f"./A/{i}", v) for i, v in enumerate(repo_values)]
        }
        with patch.object(
            self.module, "update_downstream_data"
        ) as update, patch.object(self.module, "update_diff_data"):
            self.module._handle_custom_windows_device_configuration(
                intune_data, repo_data
            )
        return update.called

    def test_patches_when_only_the_first_setting_differs(self):
        """A change to a setting that is not the last one must be patched."""
        self.assertTrue(self._patched(["old", "same"], ["new", "same"]))

    def test_patches_when_only_the_last_setting_differs(self):
        """A change to the last setting is patched."""
        self.assertTrue(self._patched(["same", "old"], ["same", "new"]))

    def test_patches_when_a_setting_is_added(self):
        """A setting added to the end of the profile must be patched."""
        self.assertTrue(self._patched(["same"], ["same", "added"]))

    def test_no_patch_when_nothing_differs(self):
        """An unchanged profile is not patched."""
        self.assertFalse(self._patched(["same", "same"], ["same", "same"]))


if __name__ == "__main__":
    unittest.main()
