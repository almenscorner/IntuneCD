import unittest
from unittest.mock import patch
from src.IntuneCD.backup.Intune.Activationlock import ActivationLockBackupModule


class TestActivationLockBackupModule(unittest.TestCase):
    """A class to test the ActivationLockBackupModule class"""

    def setUp(self):
        self.module = ActivationLockBackupModule()

    @patch.object(ActivationLockBackupModule, "make_graph_request")
    @patch.object(ActivationLockBackupModule, "batch_request")
    @patch.object(ActivationLockBackupModule, "process_data")
    def test_main(self, mock_process_data, mock_batch_request, mock_make_graph_request):
        """Test that the main method gets the graph data and processes it correctly"""
        mock_make_graph_request.return_value = {"value": [{"id": "device1"}]}
        mock_batch_request.return_value = [{"activationLockBypassCode": "code1"}]

        self.module.main()

        mock_make_graph_request.assert_called_once_with(
            endpoint=self.module.endpoint + self.module.CONFIG_ENDPOINT,
            params={
                "$select": "id",
                "$filter": "startsWith(operatingSystem, 'macOS') or startsWith(operatingSystem, 'iOS') or startsWith(operatingSystem, 'iPadOS')",
            },
        )
        mock_batch_request.assert_called_once_with(
            ["device1"],
            "deviceManagement/managedDevices/",
            "?$select=id,deviceName,serialNumber,activationLockBypassCode",
        )
        mock_process_data.assert_called_once_with(
            data=[{"activationLockBypassCode": "code1"}],
            filetype=self.module.filetype,
            path=self.module.path,
            name_key=None,
            log_message=None,
        )

    @patch.object(ActivationLockBackupModule, "make_graph_request")
    @patch.object(ActivationLockBackupModule, "log")
    def test_main_logs_exception_graph_data(self, mock_log, mock_make_graph_request):
        """Test that the main method logs an exception when an exception is raised getting the graph data"""
        mock_make_graph_request.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg=f"Error getting Activation Lock data from {self.module.endpoint + self.module.CONFIG_ENDPOINT}: Test exception"
        )

    @patch.object(ActivationLockBackupModule, "process_data")
    @patch.object(ActivationLockBackupModule, "make_graph_request")
    @patch.object(ActivationLockBackupModule, "batch_request")
    @patch.object(ActivationLockBackupModule, "log")
    def test_main_logs_exception_process_data(
        self, mock_log, mock_batch_request, mock_make_graph_request, mock_process_data
    ):
        """Test that the main method logs an exception when an exception is raised processing the graph data"""
        mock_make_graph_request.return_value = {"value": [{"id": "device1"}]}
        mock_batch_request.return_value = [{"activationLockBypassCode": "code1"}]
        mock_process_data.side_effect = Exception("Test exception")

        self.module.main()

        mock_log.assert_called_with(
            msg="Error processing Activation Lock data: Test exception"
        )


if __name__ == "__main__":
    unittest.main()
