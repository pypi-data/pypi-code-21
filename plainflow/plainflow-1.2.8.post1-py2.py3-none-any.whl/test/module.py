import unittest

import plainflow


class TestModule(unittest.TestCase):

    def failed(self):
        self.failed = True

    def setUp(self):
        self.failed = False
        plainflow.secret_key = 'testsecret'
        plainflow.on_error = self.failed

    def test_no_secret_key(self):
        plainflow.secret_key = None
        self.assertRaises(Exception, plainflow.track)

    def test_no_host(self):
        plainflow.host = None
        self.assertRaises(Exception, plainflow.track)

    def test_track(self):
        plainflow.track('userId', 'python module event')
        plainflow.flush()

    def test_identify(self):
        plainflow.identify('userId', {'email': 'user@email.com'})
        plainflow.flush()

    def test_group(self):
        plainflow.group('userId', 'groupId')
        plainflow.flush()

    def test_alias(self):
        plainflow.alias('previousId', 'userId')
        plainflow.flush()

    def test_page(self):
        plainflow.page('userId')
        plainflow.flush()

    def test_screen(self):
        plainflow.screen('userId')
        plainflow.flush()

    def test_flush(self):
        plainflow.flush()
