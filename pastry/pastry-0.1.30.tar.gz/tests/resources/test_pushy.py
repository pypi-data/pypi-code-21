import mock
import unittest

from pastry.resources.pushy import Pushy


class PushyTestCase(unittest.TestCase):

    @mock.patch('pastry.resources.pushy.Pushy.base_url', return_value='base')
    @mock.patch('pastry.resources.pushy.PastryClient.call', return_value={})
    def test_exists(self, call, base_url):
        self.assertEqual(Pushy.status('node'), {})
        call.assert_called_with('base/node_states/node')
