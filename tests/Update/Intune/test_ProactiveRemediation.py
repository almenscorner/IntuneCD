# -*- coding: utf-8 -*-
import os
import tempfile
import unittest
from unittest.mock import patch

from src.IntuneCD.update.Intune.ProactiveRemediation import (
    ProactiveRemediationUpdateModule,
)


class TestProactiveRemediationUpdateModule(unittest.TestCase):
    """Tests for the ProactiveRemediationUpdateModule class."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.module = ProactiveRemediationUpdateModule(path=self.temp_dir.name)
        os.makedirs(self.module.script_data_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_script(self, filename: str, content: str) -> None:
        with open(
            f"{self.module.script_data_path}{filename}", "w", encoding="utf-8"
        ) as f:
            f.write(content)

    def test_get_script_data_matches_filename_prefix_without_append_id(self):
        """Test that scripts are matched by policy name when filenames have no id."""
        script_files = [
            "Policy A_detectionScript.ps1",
            "Policy A_remediationScript.ps1",
            "Policy A Extra_detectionScript.ps1",
            "Policy A Extra_remediationScript.ps1",
            "Policy B_detectionScript.ps1",
            "Policy B_remediationScript.ps1",
        ]
        for script_file in script_files:
            self._write_script(script_file, script_file)

        with patch(
            "src.IntuneCD.update.Intune.ProactiveRemediation.os.listdir",
            return_value=script_files,
        ):
            detection_script, remediation_script = self.module._get_script_data(
                "Policy A.yaml"
            )

        self.assertEqual(detection_script, "Policy A_detectionScript.ps1")
        self.assertEqual(remediation_script, "Policy A_remediationScript.ps1")

    def test_get_script_data_matches_id_with_append_id(self):
        """Test that scripts are matched by id when filenames have appended ids."""
        script_files = [
            "Policy A_detectionScript__policy-a-id.ps1",
            "Policy A_remediationScript__policy-a-id.ps1",
            "Policy B_detectionScript__policy-b-id.ps1",
            "Policy B_remediationScript__policy-b-id.ps1",
        ]
        for script_file in script_files:
            self._write_script(script_file, script_file)

        with patch(
            "src.IntuneCD.update.Intune.ProactiveRemediation.os.listdir",
            return_value=script_files,
        ):
            detection_script, remediation_script = self.module._get_script_data(
                "Policy A__policy-a-id.yaml"
            )

        self.assertEqual(detection_script, "Policy A_detectionScript__policy-a-id.ps1")
        self.assertEqual(
            remediation_script, "Policy A_remediationScript__policy-a-id.ps1"
        )

    def test_get_script_data_handles_double_underscore_without_append_id(self):
        """Test that double underscores in policy names are not treated as ids."""
        script_files = [
            "Policy__A_detectionScript.ps1",
            "Policy__A_remediationScript.ps1",
            "Policy B_detectionScript__A.ps1",
            "Policy B_remediationScript__A.ps1",
        ]
        for script_file in script_files:
            self._write_script(script_file, script_file)

        with patch(
            "src.IntuneCD.update.Intune.ProactiveRemediation.os.listdir",
            return_value=script_files,
        ):
            detection_script, remediation_script = self.module._get_script_data(
                "Policy__A.yaml"
            )

        self.assertEqual(detection_script, "Policy__A_detectionScript.ps1")
        self.assertEqual(remediation_script, "Policy__A_remediationScript.ps1")


if __name__ == "__main__":
    unittest.main()
