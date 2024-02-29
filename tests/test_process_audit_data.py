# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.intunecdlib.process_audit_data import (
    _check_if_git_repo,
    _configure_git,
    _get_payload_from_audit_data,
    _git_check_modified,
    _git_check_new_file,
    _git_commit_changes,
    _git_installed,
    process_audit_data,
)


class TestProcessAuditData(unittest.TestCase):
    """
    Test process audit data
    """

    @patch("src.IntuneCD.intunecdlib.process_audit_data.subprocess.run")
    def test_configure_git(self, mock_run):
        """
        Test configure git
        """
        self.record = {
            "activityDateTime": "2021-05-25T20:00:00Z",
            "activityResourceType": "test",
            "userPrincipalName": "test",
            "actor": "test",
        }
        mock_run.return_value.returncode = 0
        self.assertIsNone(_configure_git(self.record, "path"))

    @patch("src.IntuneCD.intunecdlib.process_audit_data.subprocess.run")
    def test_git_installed(self, mock_run):
        """
        Test git installed
        """
        mock_run.return_value.returncode = 0
        self.assertTrue(_git_installed())

        mock_run.return_value.returncode = 1
        self.assertFalse(_git_installed())

    @patch("src.IntuneCD.intunecdlib.process_audit_data.subprocess.run")
    def test_check_if_git_repo(self, mock_run):
        """
        Test check if git repo
        """
        mock_run.return_value.stdout = "true"
        self.assertTrue(_check_if_git_repo("path", "file"))

        mock_run.return_value.stdout = "false"
        self.assertFalse(_check_if_git_repo("path", "file"))

    @patch("src.IntuneCD.intunecdlib.process_audit_data.subprocess.run")
    def test_git_check_modified(self, mock_run):
        """
        Test git check modified
        """
        mock_run.return_value.stdout = "modified"
        self.assertTrue(_git_check_modified("path", "file"))

        mock_run.return_value.stdout = ""
        self.assertFalse(_git_check_modified("path", "file"))

    @patch("src.IntuneCD.intunecdlib.process_audit_data.subprocess.run")
    def test_git_check_new_file(self, mock_run):
        """
        Test git check new file
        """
        mock_run.return_value.stderr = "did not match any file(s) known to git"
        self.assertTrue(_git_check_new_file("path", "file"))

        mock_run.return_value.stderr = ""
        self.assertFalse(_git_check_new_file("path", "file"))

    @patch("src.IntuneCD.intunecdlib.process_audit_data.subprocess.run")
    def test_git_commit_changes(self, mock_run):
        """
        Test git commit changes
        """
        mock_run.return_value.returncode = 0
        self.record = {
            "activityDateTime": "2021-05-25T20:00:00Z",
            "auditResourceType": "test",
            "userPrincipalName": "test",
            "actor": "test",
            "activityOperationType": "test",
            "activityResult": "test",
        }
        self.assertIsNone(_git_commit_changes(self.record, "path", "file"))

        mock_run.return_value.returncode = 1
        self.assertIsNone(_git_commit_changes(self.record, "path", "file"))

    def test_get_payload_from_audit_data(self):
        """
        Test get payload from audit data
        """
        self.record = [
            {
                "activityDateTime": "2021-05-25T20:00:00Z",
                "userPrincipalName": "test",
                "actor": "test",
                "activityOperationType": "test",
                "activityResult": "test",
                "test": "test",
            }
        ]
        self.compare_data = {"type": "test", "value": "test"}

        self.assertIsNotNone(
            _get_payload_from_audit_data(self.record, self.compare_data)
        )

    @patch("src.IntuneCD.intunecdlib.process_audit_data._check_if_git_repo")
    @patch("src.IntuneCD.intunecdlib.process_audit_data._configure_git")
    @patch("src.IntuneCD.intunecdlib.process_audit_data._git_installed")
    @patch("src.IntuneCD.intunecdlib.process_audit_data._get_payload_from_audit_data")
    @patch("src.IntuneCD.intunecdlib.process_audit_data._git_check_modified")
    @patch("src.IntuneCD.intunecdlib.process_audit_data._git_commit_changes")
    def test_process_audit_data(
        self,
        mock_get_payload_from_audit_data,
        mock_git_installed,
        mock_configure_git,
        mock_check_if_git_repo,
        mock_git_check_modified,
        _,
    ):
        """
        Test process audit data
        """
        mock_get_payload_from_audit_data.return_value = {
            "activityDateTime": "2021-05-25T20:00:00Z",
            "userPrincipalName": "test",
            "actor": "test",
            "activityOperationType": "test",
            "activityResult": "test",
            "test": "test",
        }
        mock_git_installed.return_value = True
        mock_check_if_git_repo.return_value = True
        self.assertIsNone(
            process_audit_data("audit_data", "compare_data", "path", "file")
        )

        mock_git_installed.return_value = False
        self.assertIsNone(
            process_audit_data("audit_data", "compare_data", "path", "file")
        )

        mock_git_installed.return_value = True
        mock_check_if_git_repo.return_value = False
        self.assertIsNone(
            process_audit_data("audit_data", "compare_data", "path", "file")
        )

        mock_git_installed.return_value = True
        mock_check_if_git_repo.return_value = True
        mock_configure_git.return_value = None
        mock_git_check_modified.return_value = "yes"

        self.assertFalse(
            process_audit_data("audit_data", "compare_data", "path", "file")
        )

    @patch("src.IntuneCD.intunecdlib.process_audit_data._check_if_git_repo")
    @patch("src.IntuneCD.intunecdlib.process_audit_data._configure_git")
    @patch("src.IntuneCD.intunecdlib.process_audit_data._git_installed")
    @patch("src.IntuneCD.intunecdlib.process_audit_data._get_payload_from_audit_data")
    def test_process_audit_data_no_record(
        self,
        mock_get_payload_from_audit_data,
        mock_git_installed,
        _,
        mock_check_if_git_repo,
    ):
        """
        Test process audit data no records
        """
        mock_get_payload_from_audit_data.return_value = {}
        mock_git_installed.return_value = True
        mock_check_if_git_repo.return_value = True

        self.assertFalse(
            process_audit_data("audit_data", "compare_data", "path", "file")
        )


if __name__ == "__main__":
    unittest.main()
