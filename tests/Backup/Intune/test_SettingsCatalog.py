# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch

from src.IntuneCD.backup.Intune.SettingsCatalog import SettingsCatalogBackupModule


class TestSettingsCatalogBackupModule(unittest.TestCase):
    """Tests for the SettingsCatalogBackupModule class."""

    def setUp(self):
        self.module = SettingsCatalogBackupModule()

    @patch.object(SettingsCatalogBackupModule, "make_graph_request")
    @patch.object(SettingsCatalogBackupModule, "batch_request")
    @patch.object(SettingsCatalogBackupModule, "make_audit_request")
    @patch.object(SettingsCatalogBackupModule, "get_object_details")
    @patch.object(SettingsCatalogBackupModule, "process_data")
    def test_main(
        self,
        mock_process_data,
        mock_get_object_details,
        mock_make_audit_request,
        mock_batch_request,
        mock_make_graph_request,
    ):
        """Test that main calls make_graph_request and process_data."""
        mock_make_graph_request.return_value = {
            "value": [{"id": "object", "name": "name", "technologies": "test"}]
        }
        mock_batch_request.return_value = {"responses": [{"id": "object"}]}
        mock_make_audit_request.return_value = {}
        mock_get_object_details.return_value = {"id": "object", "name": "name"}

        self.module.main()

        mock_make_graph_request.assert_called_once_with(
            endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT,
        )
        mock_process_data.assert_called_once_with(
            data=mock_make_graph_request.return_value["value"][0],
            filetype=None,
            path=self.module.path,
            name_key="name",
            log_message="Backing up Settings Catalog Policy: ",
            audit_compare_info={
                "type": "resourceId",
                "value_key": "id",
            },
        )

    @patch.object(SettingsCatalogBackupModule, "make_graph_request")
    @patch.object(SettingsCatalogBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that main logs an exception if make_graph_request raises an exception."""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            tag="error",
            msg=f"Error getting Settings Catalog data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception",
        )

    @patch.object(SettingsCatalogBackupModule, "make_graph_request")
    @patch.object(SettingsCatalogBackupModule, "batch_request")
    @patch.object(SettingsCatalogBackupModule, "make_audit_request")
    @patch.object(SettingsCatalogBackupModule, "get_object_details")
    @patch.object(SettingsCatalogBackupModule, "process_data")
    @patch.object(SettingsCatalogBackupModule, "log")
    def test_main_logs_exception_process_data(
        self,
        mock_log,
        mock_process_data,
        mock_get_object_details,
        mock_make_audit_request,
        mock_batch_request,
        mock_make_graph_request,
    ):
        """Test that main logs an exception if process_data raises an exception."""
        mock_make_graph_request.return_value = {
            "value": [{"id": "object", "name": "name", "technologies": "test"}]
        }
        mock_batch_request.return_value = {"responses": [{"id": "object"}]}
        mock_make_audit_request.return_value = {}
        mock_get_object_details.return_value = {"id": "object", "name": "name"}
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            tag="error", msg="Error processing Settings Catalog data: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
