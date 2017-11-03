from unittest import TestCase

import lockboxcli
from lockboxclient import LockboxClient


class TestLockboxClient(TestCase):
    def test_config(self):
        b = lockboxclient.LockboxClient()
        self.assertTrue(isinstance(b, LockboxClient))
