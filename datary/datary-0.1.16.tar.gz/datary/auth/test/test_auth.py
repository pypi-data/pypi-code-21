# -*- coding: utf-8 -*-
"""
Datary python sdk Auth test file
"""
import mock

from datary import Datary
from datary.test.test_datary import DataryTestCase
from datary.test.mock_requests import MockRequestResponse


class DataryAuthTestCase(DataryTestCase):
    """
    DataryAuth Test case
    """
    @mock.patch('datary.requests.requests.requests.post')
    def test_get_user_token(self, mock_request):
        """
        Test datary auth get_user_token
        """

        # Assert init class data & token introduced by args
        self.assertEqual(self.datary.username, self.test_username)
        self.assertEqual(self.datary.password, self.test_password)
        self.assertEqual(self.datary.token, self.test_token)
        self.assertEqual(mock_request.call_count, 0)

        # Assert get token in __init__
        mock_request.return_value = MockRequestResponse(
            "", headers={'x-set-token': self.test_token})
        self.datary = Datary(**{'username': 'pepe', 'password': 'pass'})
        self.assertEqual(mock_request.call_count, 1)

        # Assert get token by the method without args.
        mock_request.return_value = MockRequestResponse(
            "", headers={'x-set-token': self.test_token})
        token1 = self.datary.get_user_token()
        self.assertEqual(token1, self.test_token)

        # Assert get token by method     with args.
        mock_request.return_value = MockRequestResponse(
            "", headers={'x-set-token': '456'})
        token2 = self.datary.get_user_token('maria', 'pass2')
        self.assertEqual(token2, '456')

        mock_request.return_value = MockRequestResponse("", headers={})
        token3 = self.datary.get_user_token('maria', 'pass2')
        self.assertEqual(token3, '')

        self.assertEqual(mock_request.call_count, 4)

    @mock.patch('datary.requests.requests.requests.post')
    def test_properties(self, mock_request):
        """
        Test Datary auth getter/setter properties
        """

        test_token = '123'
        test_username = 'pepe'
        test_password = 'pass'
        test_commit_limit = 30

        test_token2 = '456'
        test_username2 = 'manolo'
        test_password2 = 'ssap'
        test_commit_limit2 = 30

        mock_request.return_value = MockRequestResponse(
            "", headers={'x-set-token': test_token})
        self.datary = Datary(**{
            'username': test_username,
            'password': test_password})
        self.assertEqual(mock_request.call_count, 1)

        self.assertEqual(self.datary.username, test_username)
        self.assertEqual(self.datary.password, test_password)
        self.assertEqual(self.datary.token, test_token)
        self.assertEqual(self.datary.commit_limit, test_commit_limit)
        self.assertIn(
            self.datary.token, self.datary.headers.get('Authorization'))

        self.datary.username = test_username2
        self.datary.password = test_password2
        self.datary.token = test_token2
        self.datary.commit_limit = test_commit_limit2

        self.assertEqual(self.datary.username, test_username2)
        self.assertEqual(self.datary.password, test_password2)
        self.assertEqual(self.datary.token, test_token2)
        self.assertEqual(self.datary.commit_limit, test_commit_limit2)
        self.assertIn(
            self.datary.token, self.datary.headers.get('Authorization'))

        # no username sig-in
        self.datary.username = None
        self.datary.token = None
        self.datary.sign_in()
        self.assertEqual(self.datary.token, None)

        # no password sig-in
        self.datary.username = 'pepe'
        self.datary.password = None
        self.datary.token = None
        self.datary.sign_in()
        self.assertEqual(self.datary.token, None)

    @mock.patch('datary.requests.requests.requests.get')
    def test_sign_out(self, mock_request):
        """
        Test datary auth sign_out
        """

        # Fail sign out
        mock_request.return_value = MockRequestResponse(
            "Err", status_code=500)
        self.datary.sign_out()
        self.assertEqual(self.datary.token, self.test_token)
        self.assertEqual(mock_request.call_count, 1)

        # reset mock
        mock_request.reset_mock()

        # Succes sign out
        mock_request.return_value = MockRequestResponse(
            "OK", status_code=200)

        self.assertEqual(self.datary.token, self.test_token)
        self.datary.sign_out()
        self.assertEqual(self.datary.token, None)
        self.assertEqual(mock_request.call_count, 1)
