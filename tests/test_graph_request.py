#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module tests the graph_request module.
"""

import unittest
from unittest import mock
from unittest.mock import patch

from src.IntuneCD.intunecdlib.graph_request import (
    makeapirequest,
    makeapirequestDelete,
    makeapirequestPatch,
    makeapirequestPost,
    makeapirequestPut,
    makeAuditRequest,
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


@patch("src.IntuneCD.intunecdlib.graph_request.makeapirequest")
@patch("requests.get")
@patch("time.sleep", return_value=None)
class TestGraphRequestGet(unittest.TestCase):
    """Test class for graph_request."""

    def setUp(self):
        self.token = {"access_token": "token"}

    def test_makeapirequest_status_429_no_q_param(self, _, mock_get, __):
        """The request should be made once and exception should be raised."""
        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(
                self,
                status=429,
                content="Too Many equests",
                headers={"Retry-After": "10"},
            )
            self.mock_resp2 = _mock_response(self, status=200, content="Success")
            mock_get.side_effect = self.mock_resp, self.mock_resp2
            makeapirequest("https://endpoint", self.token)

        self.assertEqual(2, mock_get.call_count)

    def test_makeapirequest_status_429_with_q_param(self, _, mock_get, __):
        """The request should be made once and exception should be raised."""
        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(
                self,
                status=429,
                content="Too Many Requests",
                headers={"Retry-After": "10"},
            )
            self.mock_resp2 = _mock_response(self, status=200, content="Success")
            mock_get.side_effect = self.mock_resp, self.mock_resp2
            makeapirequest("https://endpoint", self.token, q_param="$filter=id eq '0'")

        self.assertEqual(2, mock_get.call_count)

    def test_makeapirequest_no_q_param(self, _, mock_get, __):
        """The request should be made once and the response should be returned."""
        self.mock_resp = _mock_response(
            self, status=200, content='{"value": [{"id": "0"}]}'
        )
        mock_get.return_value = self.mock_resp
        self.result = makeapirequest("https://endpoint", self.token)
        self.assertEqual(self.result, {"value": [{"id": "0"}]})

    def test_makeapirequest_status_502_no_q_param(self, _, mock_get, __):
        """The request should be made twice and exception should be raised."""
        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=502, content="request timeout")
            mock_get.return_value = self.mock_resp
            makeapirequest("https://endpoint", self.token)

        self.assertEqual(4, mock_get.call_count)

    def test_makeapirequest_status_503_no_q_param(self, _, mock_get, __):
        """The request should be made twice and exception should be raised."""
        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=503, content="request timeout")
            mock_get.return_value = self.mock_resp
            makeapirequest("https://endpoint", self.token)

        self.assertEqual(4, mock_get.call_count)

    def test_makeapirequest_status_504_no_q_param(self, _, mock_get, __):
        """The request should be made twice and exception should be raised."""
        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=504, content="request timeout")
            mock_get.return_value = self.mock_resp
            makeapirequest("https://endpoint", self.token)

        self.assertEqual(4, mock_get.call_count)

    def test_makeapirequest_with_q_param(self, _, mock_get, __):
        """The request should be made once and the response should be returned."""
        self.mock_resp = _mock_response(
            self, status=200, content='{"value": [{"id": "0"}]}'
        )
        mock_get.return_value = self.mock_resp
        self.result = makeapirequest(
            "https://endpoint", self.token, q_param="$filter=id eq '0'"
        )
        self.assertEqual(self.result, {"value": [{"id": "0"}]})

    def test_makeapirequest_status_502_with_q_param(self, _, mock_get, __):
        """The request should be made twice and exception should be raised."""
        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=502, content="request timeout")
            mock_get.return_value = self.mock_resp
            makeapirequest("https://endpoint", self.token, q_param="$filter=id eq '0'")

        self.assertEqual(2, mock_get.call_count)

    def test_makeapirequest_status_503_with_q_param(self, _, mock_get, __):
        """The request should be made twice and exception should be raised."""
        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=503, content="request timeout")
            mock_get.return_value = self.mock_resp
            makeapirequest("https://endpoint", self.token, q_param="$filter=id eq '0'")

        self.assertEqual(2, mock_get.call_count)

    def test_makeapirequest_status_504_with_q_param(self, _, mock_get, __):
        """The request should be made twice and exception should be raised."""
        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=504, content="request timeout")
            mock_get.return_value = self.mock_resp
            makeapirequest("https://endpoint", self.token, q_param="$filter=id eq '0'")

        self.assertEqual(2, mock_get.call_count)

    def test_makeapirequest_odata_nextlink(self, _, mock_get, mock_makeapirequest):
        """The request should be made and the response should contain next link values."""
        self.NEXT_LINK_VALUE = {"value": [{"id": "1"}]}
        mock_makeapirequest.return_value = self.NEXT_LINK_VALUE
        self.mock_resp = _mock_response(
            self,
            status=200,
            content='{"value": [{"id": "0"}], "@odata.nextLink": "https://endpoint"}',
        )
        mock_get.return_value = self.mock_resp
        self.result = makeapirequest("https://endpoint", self.token)

        self.assertEqual(self.result["value"], [{"id": "0"}, {"id": "1"}])

    def test_makeapirequest_status_404(self, _, mock_get, __):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=404, content="not found")
        mock_get.return_value = self.mock_resp
        makeapirequest("https://endpoint", self.token)

        self.assertEqual(1, mock_get.call_count)

    def test_makeapirequest_assignmentfilter_not_enabled(self, _, mock_get, __):
        """The request should be made and assignment filters should be skipped."""
        self.mock_resp = _mock_response(
            self, status=500, content='{"FeatureNotEnabled": []}'
        )
        mock_get.return_value = self.mock_resp
        makeapirequest("https://endpoint/assignmentFilters", self.token)

        self.assertEqual(1, mock_get.call_count)

    def test_makeapirequest_exception(self, _, mock_get, __):
        """The request should be made and exception should be raised."""
        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(
                self, status=500, content="Internal Server Error"
            )
            mock_get.return_value = self.mock_resp
            makeapirequest("https://endpoint/", self.token)

        self.assertEqual(1, mock_get.call_count)


@patch("src.IntuneCD.intunecdlib.graph_request.makeapirequestPatch")
@patch("requests.patch")
class TestGraphRequestPatch(unittest.TestCase):
    """Test class for graph_request."""

    def setUp(self):
        self.token = {"access_token": "token"}

    def test_makeapirequestPatch_no_q_param(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=200, content="")
        mock_patch.return_value = self.mock_resp

        self.assertEqual(
            makeapirequestPatch(
                "https://endpoint", self.token, q_param=None, jdata='{"id": "0"}'
            ),
            None,
        )

    def test_makeapirequestPatch_with_q_param(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=200, content="")
        mock_patch.return_value = self.mock_resp

        self.assertEqual(
            makeapirequestPatch(
                "https://endpoint",
                self.token,
                q_param="$filter=id eq '0'",
                jdata='{"id": "0"}',
            ),
            None,
        )

    def test_makeapirequestPatch_not_matching_status_code(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=204, content="")
            mock_patch.return_value = self.mock_resp
            makeapirequestPatch(
                "https://endpoint",
                self.token,
                q_param="$filter=id eq '0'",
                jdata='{"id": "0"}',
                status_code=200,
            )

        self.assertEqual(1, mock_patch.call_count)


@patch("src.IntuneCD.intunecdlib.graph_request.makeapirequestPost")
@patch("requests.post")
@patch("time.sleep", return_value=None)
class TestGraphRequestPost(unittest.TestCase):
    """Test class for graph_request."""

    def setUp(self):
        self.token = {"access_token": "token"}
        self.jdata = {"id": "0"}
        self.content = '{"id": "0"}'
        self.expected_result = {"id": "0"}

    def test_makeapirequestPost_status_429_no_q_param(self, _, mock_patch, __):
        """The request should be made twice."""
        self.mock_resp = _mock_response(
            self, status=429, content="Too Many equests", headers={"Retry-After": "10"}
        )
        self.mock_resp2 = _mock_response(self, status=200, content="Success")
        mock_patch.side_effect = self.mock_resp, self.mock_resp2
        makeapirequestPost("https://endpoint", self.token)

        self.assertEqual(2, mock_patch.call_count)

    def test_makeapirequestPost_status_429_with_q_param(self, _, mock_patch, __):
        """The request should be made twice."""
        self.mock_resp = _mock_response(
            self, status=429, content="Too Many Requests", headers={"Retry-After": "10"}
        )
        self.mock_resp2 = _mock_response(self, status=200, content="Success")
        mock_patch.side_effect = self.mock_resp, self.mock_resp2
        makeapirequestPost("https://endpoint", self.token, q_param="$filter=id eq '0'")

        self.assertEqual(2, mock_patch.call_count)

    def test_makeapirequestPost_status_504_no_q_param(self, _, mock_patch, __):
        """The request should be made twice."""
        self.mock_resp = _mock_response(self, status=504, content="Error")
        self.mock_resp2 = _mock_response(self, status=200, content="Success")
        mock_patch.side_effect = self.mock_resp, self.mock_resp2
        makeapirequestPost("https://endpoint", self.token)

        self.assertEqual(2, mock_patch.call_count)

    def test_makeapirequestPost_no_q_param(self, _, mock_patch, __):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=200, content=self.content)
        mock_patch.return_value = self.mock_resp
        self.result = makeapirequestPost(
            "https://endpoint", self.token, q_param=None, jdata=self.jdata
        )

        self.assertEqual(self.result, self.expected_result)

    def test_makeapirequestPost_with_q_param(self, _, mock_patch, __):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=200, content=self.content)
        mock_patch.return_value = self.mock_resp
        self.result = makeapirequestPost(
            "https://endpoint",
            self.token,
            q_param="$filter=id eq '0'",
            jdata=self.jdata,
        )

        self.assertEqual(self.result, self.expected_result)

    def test_makeapirequestPost_not_matching_status_code(self, _, mock_patch, __):
        """The request should be made and the response should be returned."""
        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=204, content="")
            mock_patch.return_value = self.mock_resp
            makeapirequestPost(
                "https://endpoint",
                self.token,
                q_param="$filter=id eq '0'",
                jdata=self.jdata,
                status_code=200,
            )

        self.assertEqual(1, mock_patch.call_count)


@patch("src.IntuneCD.intunecdlib.graph_request.makeapirequestPut")
@patch("requests.put")
class TestGraphRequestPut(unittest.TestCase):
    """Test class for graph_request."""

    def setUp(self):
        self.token = {"access_token": "token"}

    def test_makeapirequestPut_no_q_param(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=200, content="")
        mock_patch.return_value = self.mock_resp

        self.assertEqual(
            makeapirequestPut(
                "https://endpoint", self.token, q_param=None, jdata='{"id": "0"}'
            ),
            None,
        )

    def test_makeapirequestPut_with_q_param(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=200, content="")
        mock_patch.return_value = self.mock_resp

        self.assertEqual(
            makeapirequestPut(
                "https://endpoint",
                self.token,
                q_param="$filter=id eq '0'",
                jdata='{"id": "0"}',
            ),
            None,
        )

    def test_makeapirequestPut_not_matching_status_code(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=204, content="")
            mock_patch.return_value = self.mock_resp
            makeapirequestPut(
                "https://endpoint",
                self.token,
                q_param="$filter=id eq '0'",
                jdata='{"id": "0"}',
                status_code=200,
            )

        self.assertEqual(1, mock_patch.call_count)


@patch("src.IntuneCD.intunecdlib.graph_request.makeapirequestDelete")
@patch("requests.delete")
class TestGraphRequestDelete(unittest.TestCase):
    """Test class for graph_request."""

    def setUp(self):
        self.token = {"access_token": "token"}

    def test_makeapirequestDelete_no_q_param(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=200, content="")
        mock_patch.return_value = self.mock_resp

        self.assertEqual(
            makeapirequestDelete(
                "https://endpoint", self.token, q_param=None, jdata='{"id": "0"}'
            ),
            None,
        )

    def test_makeapirequestDelete_with_q_param(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(self, status=200, content="")
        mock_patch.return_value = self.mock_resp

        self.assertEqual(
            makeapirequestDelete(
                "https://endpoint",
                self.token,
                q_param="$filter=id eq '0'",
                jdata='{"id": "0"}',
            ),
            None,
        )

    def test_makeapirequestDelete_not_matching_status_code(self, mock_patch, _):
        """The request should be made and the response should be returned."""
        with self.assertRaises(Exception):
            self.mock_resp = _mock_response(self, status=204, content="")
            mock_patch.return_value = self.mock_resp
            makeapirequestDelete(
                "https://endpoint",
                self.token,
                q_param="$filter=id eq '0'",
                jdata='{"id": "0"}',
                status_code=200,
            )

        self.assertEqual(1, mock_patch.call_count)


@patch("src.IntuneCD.intunecdlib.graph_request.makeAuditRequest")
@patch("requests.get")
@patch("time.sleep", return_value=None)
class TestGraphAuditRequest(unittest.TestCase):
    """Test class for graph_request."""

    def setUp(self):
        self.token = {"access_token": "token"}

    def test_makeAuditRequest(self, _, mock_get, __):
        """The request should be made and the response should be returned."""
        self.mock_resp = _mock_response(
            self,
            status=200,
            content=(
                '{"value": [{"resources": [{"resourceId": "0", "auditResourceType": "MagicResource"}],'
                '"activityDateTime": "2021-01-01T00:00:00Z", "activityOperationType": "Patch", '
                '"activityResult": "Success", "actor": {"auditActorType": "ItPro", "userPrincipalName": "test"}}]}'
            ),
        )
        mock_get.return_value = self.mock_resp
        self.result = makeAuditRequest(
            "componentName eq 'MobileAppConfiguration'", self.token
        )
        self.assertEqual(
            self.result,
            [
                {
                    "resourceId": "0",
                    "auditResourceType": "MagicResource",
                    "actor": "test",
                    "activityDateTime": "2021-01-01T00:00:00Z",
                    "activityOperationType": "Patch",
                    "activityResult": "Success",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
