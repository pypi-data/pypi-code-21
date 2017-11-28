import responses
from unittest import TestCase

from apiconsumer import ApiConsumer


class ApiConsumerTests(TestCase):

    @responses.activate
    def test_method_unpacking(self):
        responses.add(responses.GET, 'http://api.something.com/parent/child', json={'success': True}, status=200)
        test_api = ApiConsumer(url='http://api.something.com', extra_headers={})

        response = test_api.get_parent_child()
        self.assertEqual(response, {'success': True})

    def test_unallowed_method(self):
        test_api = ApiConsumer(url='http://api.something.com', extra_headers={})

        with self.assertRaises(AttributeError):
            test_api.foo_parent_child()
