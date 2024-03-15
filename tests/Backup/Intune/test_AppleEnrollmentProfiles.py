# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.backup.Intune.AppleEnrollmentProfiles import (
    AppleEnrollmentProfilesBackupModule,
)


class TestAppleEnrollmentProfilesBackupModule(unittest.TestCase):
    """Tests for the AppleEnrollmentProfilesBackupModule class."""

    def setUp(self):
        self.module = AppleEnrollmentProfilesBackupModule()

    @patch.object(AppleEnrollmentProfilesBackupModule, "make_graph_request")
    @patch.object(AppleEnrollmentProfilesBackupModule, "batch_request")
    @patch.object(AppleEnrollmentProfilesBackupModule, "process_data")
    def test_main(self, mock_process_data, mock_batch_request, mock_make_graph_request):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.return_value = {"value": [{"id": "object"}]}
        mock_batch_request.return_value = [
            {"value": [{"id": "object"}]},
        ]

        self.module.main()

        mock_make_graph_request.assert_called_once_with(
            endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT,
        )
        mock_batch_request.assert_called_once_with(
            ["object"], "deviceManagement/depOnboardingSettings/", "/enrollmentProfiles"
        )
        mock_process_data.assert_called_once_with(
            data=[{"id": "object"}],
            filetype=None,
            path="None/Enrollment Profiles/Apple/",
            name_key="displayName",
            log_message="Backing up Apple Enrollment Profile: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(AppleEnrollmentProfilesBackupModule, "make_graph_request")
    @patch.object(AppleEnrollmentProfilesBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg=f"Error getting Apple Enrollment Profile data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception"
        )

    @patch.object(AppleEnrollmentProfilesBackupModule, "process_data")
    @patch.object(AppleEnrollmentProfilesBackupModule, "make_graph_request")
    @patch.object(AppleEnrollmentProfilesBackupModule, "log")
    @patch.object(AppleEnrollmentProfilesBackupModule, "batch_request")
    def test_main_logs_exception_process_data(
        self, mock_batch_request, mock_log, mock_make_graph_request, mock_process_data
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.return_value = {"value": [{"id": "object"}]}
        mock_batch_request.return_value = [
            {"value": [{"id": "object"}]},
        ]
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg="Error processing Apple Enrollment Profile data: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
