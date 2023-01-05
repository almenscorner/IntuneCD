#!/usr/bin/env python3

"""
This module tests the update_frontend function.
"""

import unittest

from unittest import mock
from unittest.mock import patch
from src.IntuneCD.update_frontend import update_frontend


def _mock_response(self, status=200, content="CONTENT", json_data=None, raise_for_status=None):
    """Mock the response on the requests module."""

    mock_resp = mock.Mock()
    # mock raise_for_status call w/optional error
    mock_resp.raise_for_status = mock.Mock()
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status
    # set status code and content
    mock_resp.status_code = status
    mock_resp.text = content

    return mock_resp


@patch("src.IntuneCD.update_frontend.update_frontend")
@patch("requests.post")
class TestUpdateFrontend(unittest.TestCase):
    def test_update_env_configured(self, mock_post, mock_update_frontend):
        """
        Test that the update_frontend function is called with the correct parameters.
        """

        self.mock_resp = _mock_response(self, status=200, content="")
        mock_post.return_value = self.mock_resp

        with patch.dict("os.environ", {"API_KEY": "test"}):
            self.update = update_frontend("http://localhost:8080/update", {"configurations": 1})

            mock_post.assert_called_once_with(
                "http://localhost:8080/update", json={"configurations": 1}, headers={"X-API-Key": "test"}
            )

    def test_update_env_not_configured(self, mock_post, mock_update_frontend):
        """If the API_KEY is not configured, the function should raise an exception."""
        with patch.dict("os.environ", {}):
            self.assertRaises(Exception, update_frontend, "http://localhost:8080/update", {"configurations": 1})

    def test_update_frontend_error(self, mock_post, mock_update_frontend):
        """If the update failed the function should raise an exception."""

        self.mock_resp = _mock_response(self, status=500, content="Internal Server Error")
        mock_post.return_value = self.mock_resp

        with patch.dict("os.environ", {"API_KEY": "test"}):
            self.assertRaises(Exception, update_frontend, "http://localhost:8080/update", {"configurations": 1})


if __name__ == "__main__":
    unittest.main()
