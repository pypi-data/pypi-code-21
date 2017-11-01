import requests
import json
import six

from globus_sdk.response import GlobusResponse, GlobusHTTPResponse
from tests.framework import CapturedIOTestCase


class GlobusResponseTests(CapturedIOTestCase):

    def setUp(self):
        """
        Makes GlobusResponses wrapped around known data for testing
        """
        super(GlobusResponseTests, self).setUp()
        self.dict_data = {"label1": "value1", "label2": "value2"}
        self.dict_response = GlobusResponse(self.dict_data)

        self.list_data = ["value1", "value2", "value3"]
        self.list_response = GlobusResponse(self.list_data)

    def test_data(self):
        """
        Gets the data from the GlobusResponses, confirms results
        """
        self.assertEqual(self.dict_response.data, self.dict_data)
        self.assertEqual(self.dict_response.data, self.dict_data)

    def test_str(self):
        """
        Confirms that individual values are seen in data
        """
        for item in self.dict_data:
            self.assertTrue(item in self.dict_response)
        self.assertFalse("nonexistant" in self.dict_response)

        for item in self.list_data:
            self.assertTrue(item in self.list_response)
        self.assertFalse("nonexistant" in self.list_response)

    def test_getitem(self):
        """
        Confirms that values can be accessed from the GlobusResponse
        """
        for key in self.dict_data:
            self.assertEqual(self.dict_response[key], self.dict_data[key])

        for i in range(len(self.list_data)):
            self.assertEqual(self.list_response[i], self.list_data[i])

    def test_contains(self):
        """
        Confirms that individual values are seen in the GlobusResponse
        """
        for item in self.dict_data:
            self.assertTrue(item in self.dict_response)
        self.assertFalse("nonexistant" in self.dict_response)

        for item in self.list_data:
            self.assertTrue(item in self.list_response)
        self.assertFalse("nonexistant" in self.list_response)

    def test_get(self):
        """
        Gets individual values from dict response, confirms results
        Confirms list response correctly fails as non indexable
        """
        for item in self.dict_data:
            self.assertEqual(self.dict_response.get(item),
                             self.dict_data.get(item))

        with self.assertRaises(AttributeError):
            self.list_response.get("value1")


class GlobusHTTPResponseTests(CapturedIOTestCase):

    def setUp(self):
        """
        Makes GlobusHTTPResponses wrapped around HTTP responses for testing
        Uses responses with well formed json, malformed json, and plain text
        """
        super(GlobusHTTPResponseTests, self).setUp()

        # well formed json
        self.json_data = {"label1": "value1", "label2": "value2"}
        json_response = requests.Response()
        json_response._content = six.b(json.dumps(self.json_data))
        json_response.headers["Content-Type"] = "application/json"
        self.globus_json_response = GlobusHTTPResponse(json_response)

        # malformed json
        malformed_response = requests.Response()
        malformed_response._content = six.b("{")
        malformed_response.headers["Content-Type"] = "application/json"
        self.globus_malformed_response = GlobusHTTPResponse(malformed_response)

        # text
        self.text_data = "text data"
        text_response = requests.Response()
        text_response._content = six.b(self.text_data)
        text_response.headers["Content-Type"] = "text/plain"
        self.globus_text_response = GlobusHTTPResponse(text_response)

    def test_data(self):
        """
        Gets the data from each HTTPResponse, confirms expected data from json
        and None from malformed or plain text HTTP
        """
        # well formed json
        self.assertEqual(self.globus_json_response.data, self.json_data)
        # malformed json
        self.assertEqual(self.globus_malformed_response.data, None)
        # text
        self.assertEqual(self.globus_text_response.data, None)

    def test_text(self):
        """
        Gets the text from each HTTPResponse, confirms expected results
        """
        # well formed json
        self.assertEqual(self.globus_json_response.text,
                         json.dumps(self.json_data))
        # malformed json
        self.assertEqual(self.globus_malformed_response.text, "{")
        # text
        self.assertEqual(self.globus_text_response.text, self.text_data)
