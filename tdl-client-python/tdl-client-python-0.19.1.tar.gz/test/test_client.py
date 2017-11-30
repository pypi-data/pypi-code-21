__author__ = 'tdpreece'

import unittest

from tdl.client import Client

class TestClient(unittest.TestCase):
    def test_if_user_goes_live_client_should_process_all_messages(self):
        client = Client('localhost', 21613, 'test')
