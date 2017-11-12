from unittest import TestCase
from kotp import kotp

class TestKeyringOTP(TestCase):

    def test_run(self):
        kotp.KeyringOTP("SECRETS", console_output=True, run_duration=0.1).run()
