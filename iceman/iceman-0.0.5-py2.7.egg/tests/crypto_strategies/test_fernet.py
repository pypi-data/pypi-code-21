import pytest
from random_words import RandomWords

from iceman.crypto_strategies.fernet import Fernet

class TestInstance(object):
    def test_instantiation(self):
        subject = Fernet('foo')
        assert subject.__class__.__name__ == 'Fernet'

class TestIntegration(object):
    def test_integration(self):
        words = RandomWords().random_words(count=5449)

        preshared_key = 'foo'
        cipher_suite = Fernet(preshared_key)

        for word in words:
            enc = cipher_suite.encrypt(word)
            dec = cipher_suite.decrypt(enc)
            assert word == dec
