from iceman.configuration import Configuration
from iceman.traffic.ingress import Ingress

class TestInstance(object):

    def test_instance(self):
        config = Configuration()
        config.cipher_suite = config.initialize_cipher_suite('fernet')

        subject = Ingress(config.cipher_suite, config.encryption_enabled)
        assert subject.__class__.__name__ == 'Ingress'
        assert subject.callback != None
        assert subject.QUEUE != None
        assert subject.queue == subject.QUEUE
        assert subject.cipher_suite == config.cipher_suite
        assert subject.encryption_enabled == config.encryption_enabled
