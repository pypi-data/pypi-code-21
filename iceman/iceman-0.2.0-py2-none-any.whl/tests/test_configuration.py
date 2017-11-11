import os

from iceman.configuration import Configuration
from iceman.interceptor import Interceptor

class TestInstance(object):
    def test_instantiation(self):
        subject = Configuration()
        assert subject.__class__.__name__ == 'Configuration'

class TestCipherSuite(object):
    def test_cipher_suites(self):
        obj = Configuration()
        for strategy in obj.CRYPTO_STRATEGIES:
            obj.cipher_suite = obj.initialize_cipher_suite(strategy)
            subject = obj.cipher_suite
            assert subject != None
            assert hasattr(subject, 'encrypt')
            assert hasattr(subject, 'decrypt')

class TestConfiguration(object):
    def test_namespace(self):
        subject = Configuration()
        assert subject.NAMESPACE == 'interceptor'

    def test_settings(self):
        subject = Configuration().get_settings()
        assert subject.__class__.__name__ == 'ConfigParser'

    def test_encryption_enabled_true(self):
        subject = Configuration().encryption_enabled
        assert subject.__class__.__name__ == 'bool'
        assert subject

    def test_encryption_enabled_false(self):
        value = os.environ['ICEMAN_ENCRYPTION_ENABLED']

        os.environ['ICEMAN_ENCRYPTION_ENABLED'] = 'false'
        subject = Configuration().encryption_enabled
        assert not subject

        os.environ['ICEMAN_ENCRYPTION_ENABLED'] = 'foo'
        subject = Configuration().encryption_enabled
        assert not subject

        os.environ['ICEMAN_ENCRYPTION_ENABLED'] = value

    def test_crypto_strategies(self):
        subject = Configuration().CRYPTO_STRATEGIES
        assert subject.__class__.__name__ == 'list'
        assert len(subject) == 2
        assert 'icemicro' in subject
        assert 'fernet' in subject

    def test_queues(self):
        subject = Configuration().QUEUES
        assert subject.__class__.__name__ == 'list'
        assert len(subject) == 2
        assert 'egress' in subject
        assert 'ingress' in subject
