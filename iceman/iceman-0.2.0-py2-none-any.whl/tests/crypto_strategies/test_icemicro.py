import pytest
from random_words import RandomWords

from iceman.configuration import Configuration
from iceman.crypto_strategies.icemicro import Icemicro

class TestInstance(object):
    def test_instantiation(self):
        subject = Icemicro('foo')
        assert subject.__class__.__name__ == 'Icemicro'

class TestIntegration(object):
    def test_integration(self):

        config = Configuration()
        crypto_strategy = 'icemicro'
        config.cipher_suite = config.initialize_cipher_suite(crypto_strategy)

        words = RandomWords().random_words(count=5449)
        for word in words:
            cipher_suite = config.cipher_suite
            enc = cipher_suite.encrypt(word)
            dec = cipher_suite.decrypt(enc)
            assert word == dec

    def test_instantiation(self):

        import os, random, string
        preshared_key = os.environ['ICEMAN_PRESHARED_KEY']
        os.environ['ICEMAN_PRESHARED_KEY'] = ''.join(random.choice(string.lowercase) for x in range(4097))
        config = Configuration()
        crypto_strategy = 'icemicro'
        config.cipher_suite = config.initialize_cipher_suite(crypto_strategy)

        words = RandomWords().random_words(count=5449)
        for word in words:
            cipher_suite = config.cipher_suite
            enc = cipher_suite.encrypt(word)
            dec = cipher_suite.decrypt(enc)
            assert word == dec

        os.environ['ICEMAN_PRESHARED_KEY'] = preshared_key
