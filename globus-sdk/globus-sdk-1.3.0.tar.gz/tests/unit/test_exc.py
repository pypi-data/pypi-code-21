import requests
import json
import six

from globus_sdk.exc import (GlobusAPIError, TransferAPIError, AuthAPIError,
                            GlobusOptionalDependencyError,
                            NetworkError, GlobusTimeoutError,
                            GlobusConnectionError, convert_request_exception)
from tests.framework import CapturedIOTestCase


# super class for Globus, Auth, and Transfer APIError tests with shared setup
class APIErrorTests(CapturedIOTestCase):

    __test__ = False  # prevents base class from trying to run tests

    def setUp(self):
        """
        Creates a json error response a text error response, and a malformed
        json response for testing
        """
        super(APIErrorTests, self).setUp()

        self.json_data = {"errors": [{"message": "json error message",
                                      "code": "Json Error"}]}
        self.json_response = requests.Response()
        self.json_response._content = six.b(json.dumps(self.json_data))
        self.json_response.headers["Content-Type"] = "application/json"
        self.json_response.status_code = "400"

        self.text_data = "error message"
        self.text_response = requests.Response()
        self.text_response._content = six.b(self.text_data)
        self.text_response.headers["Content-Type"] = "text/plain"
        self.text_response.status_code = "401"

        self.malformed_response = requests.Response()
        self.malformed_response._content = six.b("{")
        self.malformed_response.headers["Content-Type"] = "application/json"
        self.malformed_response.status_code = "403"


class GlobusAPIErrorTests(APIErrorTests):

    __test__ = True  # marks sub-class as having tests

    def test_raw_json(self):
        """
        Confirms the GlobusAPIError can get raw json from the json responses,
        and defaults to text for the text response
        """
        # json
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.json_response)
        self.assertEqual(apiErr.exception.raw_json, self.json_data)

        # text
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.text_response)
        self.assertEqual(apiErr.exception.raw_json, None)

        # malformed
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.malformed_response)
        self.assertEqual(apiErr.exception.raw_json, None)

    def test_raw_text(self):
        """
        Gets raw text from both json and text responses, confirms results
        """
        # json
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.json_response)
        self.assertEqual(apiErr.exception.raw_text, json.dumps(self.json_data))

        # text
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.text_response)
        self.assertEqual(apiErr.exception.raw_text, self.text_data)

    def test_get_args(self):
        """
        Gets args from json text and malformed responses, confirms results
        Implicitly tests _load_from_json and _load_from_text
        """

        # json
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.json_response)
        expected = ("400", "Json Error", "json error message")
        self.assertEqual(apiErr.exception._get_args(), expected)

        # text
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.text_response)
        expected = ("401", "Error", "error message")
        self.assertEqual(apiErr.exception._get_args(), expected)

        # malformed
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.malformed_response)
        expected = ("403", "Error", "{")
        self.assertEqual(apiErr.exception._get_args(), expected)


class TransferAPIErrorTests(APIErrorTests):

    __test__ = True  # marks sub-class as having tests

    def setUp(self):
        """
        Creates a transfer-like json response in addition to the APIError
        setUp responses for testing
        """
        super(TransferAPIErrorTests, self).setUp()

        self.transfer_data = {"message": "transfer error message",
                              "code": "Transfer Error", "request_id": 123}
        self.transfer_response = requests.Response()
        self.transfer_response._content = six.b(json.dumps(self.transfer_data))
        self.transfer_response.headers["Content-Type"] = "application/json"
        self.transfer_response.status_code = "404"

    def test_get_args(self):
        """
        Gets args from all four response types, confirms expected results
        implicitly tests _load_from_json
        """
        # transfer
        with self.assertRaises(TransferAPIError) as apiErr:
            raise TransferAPIError(self.transfer_response)
        expected = ("404", "Transfer Error", "transfer error message", 123)
        self.assertEqual(apiErr.exception._get_args(), expected)

        # json in wrong format
        with self.assertRaises(TransferAPIError) as apiErr:
            raise TransferAPIError(self.json_response)
        expected = ("400", "Error", json.dumps(self.json_data), None)
        self.assertEqual(apiErr.exception._get_args(), expected)

        # text
        with self.assertRaises(TransferAPIError) as apiErr:
            raise TransferAPIError(self.text_response)
        expected = ("401", "Error", "error message", None)
        self.assertEqual(apiErr.exception._get_args(), expected)

        # malformed json
        with self.assertRaises(TransferAPIError) as apiErr:
            raise TransferAPIError(self.malformed_response)
        expected = ("403", "Error", "{", None)
        self.assertEqual(apiErr.exception._get_args(), expected)


class AuthAPIErrorTests(APIErrorTests):

    __test__ = True  # marks sub-class as having tests

    def setUp(self):
        """
        Creates auth-like json responses in addition to the APIError
        setUp responses for testing
        """
        super(AuthAPIErrorTests, self).setUp()

        self.simple_auth_data = {"error": "simple auth error message"}
        self.simple_auth_response = requests.Response()
        self.simple_auth_response._content = six.b(
            json.dumps(self.simple_auth_data))
        self.simple_auth_response.headers["Content-Type"] = "application/json"
        self.simple_auth_response.status_code = "404"

        self.nested_auth_data = {"errors": [
            {"detail": "nested auth error message", "code": "Auth Error"}]}
        self.nested_auth_response = requests.Response()
        self.nested_auth_response._content = six.b(
            json.dumps(self.nested_auth_data))
        self.nested_auth_response.headers["Content-Type"] = "application/json"
        self.nested_auth_response.status_code = "404"

    def test_get_args(self):
        """
        Gets args from all four response types, confirms expected results
        implicitly tests _load_from_json
        """
        # simple auth
        with self.assertRaises(AuthAPIError) as apiErr:
            raise AuthAPIError(self.simple_auth_response)
        expected = ("404", "Error", "simple auth error message")
        self.assertEqual(apiErr.exception._get_args(), expected)

        # nested auth
        with self.assertRaises(AuthAPIError) as apiErr:
            raise AuthAPIError(self.nested_auth_response)
        expected = ("404", "Auth Error", "nested auth error message")
        self.assertEqual(apiErr.exception._get_args(), expected)

        # json in wrong format
        with self.assertRaises(AuthAPIError) as apiErr:
            raise AuthAPIError(self.json_response)
        expected = ("400", "Json Error", "json error message")
        self.assertEqual(apiErr.exception._get_args(), expected)

        # text
        with self.assertRaises(AuthAPIError) as apiErr:
            raise AuthAPIError(self.text_response)
        expected = ("401", "Error", "error message")
        self.assertEqual(apiErr.exception._get_args(), expected)

        # malformed json
        with self.assertRaises(AuthAPIError) as apiErr:
            raise AuthAPIError(self.malformed_response)
        expected = ("403", "Error", "{")
        self.assertEqual(apiErr.exception._get_args(), expected)


class NetworkErrorTests(CapturedIOTestCase):

    def setUp(self):
        """
        Sets up simple exceptions to wrap
        """
        super(NetworkErrorTests, self).setUp()
        self.exc = requests.RequestException("exc_message")
        self.timeout_exc = requests.Timeout("timeout_message")
        self.connection_exc = requests.ConnectionError("connection_message")

    def test_networkError(self):
        """
        Raises a NetworkError wrapped around a RequestException
        Confirms wrapped data is available, but new message is used
        """
        msg = "wrapper message"
        with self.assertRaises(NetworkError) as err:
            raise NetworkError(msg, self.exc)

        self.assertEqual(str(err.exception), msg)
        self.assertEqual(err.exception.underlying_exception.args,
                         self.exc.args)

    def test_timeoutError(self):
        """
        Raises a GlobusTimeoutError wrapped around a request Timeout
        Confirms wrapped data is available, but new message is used
        """
        msg = "wrapper message"
        with self.assertRaises(GlobusTimeoutError) as err:
            raise GlobusTimeoutError(msg, self.timeout_exc)

        self.assertEqual(str(err.exception), msg)
        self.assertEqual(err.exception.underlying_exception.args,
                         self.timeout_exc.args)

    def test_connectionError(self):
        """
        Raises a GlobusTimeoutError wrapped around a request ConnectionError
        Confirms wrapped data is available, but new message is used
        """
        msg = "wrapper message"
        with self.assertRaises(GlobusConnectionError) as err:
            raise GlobusConnectionError(msg, self.connection_exc)

        self.assertEqual(str(err.exception), msg)
        self.assertEqual(err.exception.underlying_exception.args,
                         self.connection_exc.args)

    def test_convert_request_exception(self):
        """
        Converts known request exceptions into Globus NetworkErrors,
        confirms expected values.
        """
        # NetworkError
        conv = convert_request_exception(self.exc)
        self.assertIsInstance(conv, NetworkError)
        self.assertEqual(conv.underlying_exception.args,
                         self.exc.args)
        # Timeout Error
        conv = convert_request_exception(self.timeout_exc)
        self.assertIsInstance(conv, GlobusTimeoutError)
        self.assertEqual(conv.underlying_exception.args,
                         self.timeout_exc.args)
        # Connection Error
        conv = convert_request_exception(self.connection_exc)
        self.assertIsInstance(conv, GlobusConnectionError)
        self.assertEqual(conv.underlying_exception.args,
                         self.connection_exc.args)


class GlobusOptionalDependencyErrorTests(CapturedIOTestCase):

    def test_init(self):
        """
        Creates a GlobusOptionalDependencyError, confirms message is set
        """

        feature_name = "feature"
        dep_names = ["dep1", "dep2", "dep3"]
        with self.assertRaises(GlobusOptionalDependencyError) as depErr:
            raise GlobusOptionalDependencyError(dep_names, feature_name)
        self.assertIn("in order to use " + feature_name,
                      depErr.exception.message)
        for dep in dep_names:
            self.assertIn(dep + "\n", depErr.exception.message)
