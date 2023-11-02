#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module tests the graph_request module.
"""

import unittest
from unittest import mock
from unittest.mock import patch

import requests

from src.IntuneCD.intunecdlib.azure_request import (
    make_azure_request,
    make_azure_request_patch,
    make_azure_request_post,
    make_azure_request_put,
)


def _mock_response(
    _,
    status=200,
    content="CONTENT",
    raise_for_status=None,
    headers="",
):
    """Mock the response from the requests library."""
    mock_resp = mock.Mock()
    # mock raise_for_status call w/optional error
    mock_resp.raise_for_status = mock.Mock()
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status
    # set status code and content
    mock_resp.status_code = status
    mock_resp.text = content
    mock_resp.headers = headers

    return mock_resp


@patch("src.IntuneCD.intunecdlib.azure_request.make_azure_request")
@patch("requests.get")
@patch("time.sleep", return_value=None)
class TestMakeAzureRequestGet(unittest.TestCase):
    """Test class for graph_request."""

    def setUp(self):
        self.token = {"access_token": "token"}

    def test_make_azure_request_status_200_no_q_param(self, _, mock_get, __):
        """The request should be made once and no exception should be raised."""

        self.mock_resp = _mock_response(
            self, status=200, content='{"value": [{"id": "0"}]}'
        )
        mock_get.return_value = self.mock_resp
        make_azure_request(self.token, "SomeEndpoint")

        self.assertEqual(1, mock_get.call_count)

    def test_make_azure_request_status_200_with_q_param(self, _, mock_get, __):
        """The request should be made once and no exception should be raised."""

        self.mock_resp = _mock_response(
            self, status=200, content='{"value": [{"id": "0"}]}'
        )
        mock_get.return_value = self.mock_resp
        make_azure_request(self.token, "SomeEndpoint", q_param="SomeParam")

        self.assertEqual(1, mock_get.call_count)

    def test_make_azure_request_status_404_no_q_param(self, _, mock_get, __):
        """The request should be made once and no exception should be raised."""

        self.mock_resp = _mock_response(self, status=404, content="")
        mock_get.return_value = self.mock_resp
        make_azure_request(self.token, "SomeEndpoint", q_param="SomeParam")

        self.assertEqual(1, mock_get.call_count)

    def test_make_azure_request_status_503_no_q_param(self, _, mock_get, __):
        """The request should be made and HTTPError should be raised."""

        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=503, content="request timeout")
            mock_get.return_value = self.mock_resp
            make_azure_request(self.token, "SomeEndpoint")

        self.assertRaises(requests.exceptions.HTTPError)


@patch("src.IntuneCD.intunecdlib.azure_request.make_azure_request_put")
@patch("requests.put")
class TestAzureRequestPut(unittest.TestCase):
    """Test class for azure_request."""

    def setUp(self):
        self.token = {"access_token": "token"}

    def test_make_azure_request_put_no_q_param(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=204, content="")
        mock_patch.return_value = self.mock_resp

        self.assertEqual(
            make_azure_request_put(self.token, "SomeEndpoint", "SomeData"),
            None,
        )

    def test_make_azure_request_put_with_q_param(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=204, content="")
        mock_patch.return_value = self.mock_resp

        self.assertEqual(
            make_azure_request_put(
                self.token, "SomeEndpoint", "SomeData", q_param="SomeParam"
            ),
            None,
        )

    def test_make_azure_request_put_not_matching_status_code(self, mock_patch, _):
        """The request should be made and HTTPError should be raised."""

        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=200, content="Error")
            mock_patch.return_value = self.mock_resp

            make_azure_request_put(self.token, "SomeEndpoint", "SomeData")

        self.assertRaises(requests.exceptions.HTTPError)


@patch("src.IntuneCD.intunecdlib.azure_request.make_azure_request_patch")
@patch("requests.patch")
class TestAzureRequestPatch(unittest.TestCase):
    """Test class for azure_request."""

    def setUp(self):
        self.token = {"access_token": "token"}

    def test_make_azure_request_patch_no_q_param(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=204, content="")
        mock_patch.return_value = self.mock_resp

        self.assertEqual(
            make_azure_request_patch(self.token, "SomeEndpoint", "SomeData"),
            None,
        )

    def test_make_azure_request_patch_with_q_param(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=204, content="")
        mock_patch.return_value = self.mock_resp

        self.assertEqual(
            make_azure_request_patch(
                self.token, "SomeEndpoint", "SomeData", q_param="SomeParam"
            ),
            None,
        )

    def test_make_azure_request_patch_not_matching_status_code(self, mock_patch, _):
        """The request should be made and HTTPError should be raised."""

        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=200, content="Error")
            mock_patch.return_value = self.mock_resp

            make_azure_request_patch(self.token, "SomeEndpoint", "SomeData")

        self.assertRaises(requests.exceptions.HTTPError)

        self.assertRaises(requests.exceptions.HTTPError)


@patch("src.IntuneCD.intunecdlib.azure_request.make_azure_request_post")
@patch("requests.post")
class TestAzureRequestPost(unittest.TestCase):
    """Test class for azure_request."""

    def setUp(self):
        self.token = {"access_token": "token"}

    def test_make_azure_request_post_no_q_param(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=204, content="")
        mock_patch.return_value = self.mock_resp

        self.assertEqual(
            make_azure_request_post(self.token, "SomeEndpoint", "SomeData"),
            None,
        )

    def test_make_azure_request_post_with_q_param(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=204, content="")
        mock_patch.return_value = self.mock_resp

        self.assertEqual(
            make_azure_request_post(
                self.token, "SomeEndpoint", "SomeData", q_param="SomeParam"
            ),
            None,
        )

    def test_make_azure_request_post_not_matching_status_code(self, mock_patch, _):
        """The request should be made and HTTPError should be raised."""

        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=200, content="Error")
            mock_patch.return_value = self.mock_resp

            make_azure_request_post(self.token, "SomeEndpoint", "SomeData")

        self.assertRaises(requests.exceptions.HTTPError)

        self.assertRaises(requests.exceptions.HTTPError)
