import pytest

from iceman.crypto_strategies.strategy import Strategy

class TestInstance(object):

    def test_instantiation(self):
        subject = Strategy()
        assert subject.__class__.__name__ == 'Strategy'
