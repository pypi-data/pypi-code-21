# -*- coding: utf-8 -*-
"""
Datary python sdk Requests test file
"""
import mock
import requests

from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryRequestsTestCase(DataryTestCase):
    """
    DataryRequests Test case
    """

    @mock.patch('datary.requests.requests.requests')
    def test_request(self, mock_requests):
        """
        Test get_request
        =============   =============   =======================================
        Parameter       Type            Description
        =============   =============   =======================================
        mock_request    mock            Mock datary.requests.requests.request
                                        function
        =============   =============   =======================================
        """

        mock_requests.get.return_value = MockRequestResponse(
            "ok", headers={'x-set-token': self.test_token})
        mock_requests.post.return_value = MockRequestResponse(
            "ok", headers={'x-set-token': self.test_token})
        mock_requests.delete.return_value = MockRequestResponse(
            "ok", headers={'x-set-token': self.test_token})

        # test GET
        result1 = self.datary.request(self.url, 'GET')
        self.assertEqual(result1.text, 'ok')

        # test POST
        result2 = self.datary.request(self.url, 'POST')
        self.assertEqual(result2.text, 'ok')

        # test deleted
        result3 = self.datary.request(self.url, 'DELETE')
        self.assertEqual(result3.text, 'ok')

        # test UNKNOWK http method
        with self.assertRaises(Exception):
            self.datary.request(self.url, 'UNKWOWN')

        # test status code wrong
        mock_requests.get.return_value = MockRequestResponse(
            "err", status_code=500)
        result4 = self.datary.request(self.url, 'GET')
        self.assertEqual(result4, None)

        mock_requests.get.side_effect = requests.RequestException('err')
        result5 = self.datary.request(self.url, 'GET')
        self.assertEqual(result5, None)

        self.assertEqual(mock_requests.get.call_count, 3)
        self.assertEqual(mock_requests.post.call_count, 1)
        self.assertEqual(mock_requests.delete.call_count, 1)
