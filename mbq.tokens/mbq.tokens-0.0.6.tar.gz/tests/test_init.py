from unittest import TestCase

from mbq import tokens
from tests import keys


class InitTest(TestCase):
    def test_init(self):
        self.assertFalse(hasattr(tokens, 'decode'))
        self.assertFalse(hasattr(tokens, 'decode_header'))

        tokens.init(certificate=keys.CERTIFICATE, allowed_audiences={'test'})

        self.assertTrue(hasattr(tokens, 'decode'))
        self.assertTrue(hasattr(tokens, 'decode_header'))

        self.assertTrue(callable(tokens.decode))
        self.assertTrue(callable(tokens.decode_header))
