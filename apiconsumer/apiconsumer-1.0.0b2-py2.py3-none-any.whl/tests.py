import responses
from unittest import TestCase

from requests import ConnectionError

from apiconsumer import ApiConsumerResponseError
from apiconsumer.exceptions import ApiConsumerRequestException
from core import ApiConsumer


class ApiConsumerTests(TestCase):

    @responses.activate
    def test_method_unpacking(self):
        responses.add(responses.GET, 'http://api.something.com/parent/child', json={'get': True}, status=200)
        responses.add(responses.POST, 'http://api.something.com/parent/child', json={'post': True}, status=201)
        test_api = ApiConsumer(url='http://api.something.com', extra_headers={})

        response = test_api.get_parent_child()
        self.assertEqual(response, {'get': True})

        response = test_api['get_parent_child']()
        self.assertEqual(response, {'get': True})

        response = test_api.get('parent_child')
        self.assertEqual(response, {'get': True})

        response = test_api.post_parent_child(data={'something': 123})
        self.assertEqual(response, {'post': True})

        response = test_api.post('parent_child', data={'something': 123})
        self.assertEqual(response, {'post': True})

    def test_unallowed_method(self):
        test_api = ApiConsumer(url='http://api.something.com', extra_headers={})

        with self.assertRaises(AttributeError):
            test_api.foo_parent_child()

    @responses.activate
    def test_return_error_response(self):
        responses.add(responses.GET, 'http://api.something.com/parent/child', status=400)
        test_api = ApiConsumer(url='http://api.something.com', extra_headers={})

        with self.assertRaises(ApiConsumerResponseError):
            test_api.get_parent_child()

    @responses.activate
    def test_requests_exception(self):
        responses.add(responses.GET, 'http://api.something.com/parent/child', body=ConnectionError(response=None, request=None))
        test_api = ApiConsumer(url='http://api.something.com', extra_headers={})

        with self.assertRaises(ApiConsumerRequestException):
            test_api.get_parent_child()

