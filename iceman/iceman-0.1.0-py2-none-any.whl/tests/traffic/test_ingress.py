from iceman.configuration import Configuration
from iceman.traffic.ingress import Ingress

class TestInstance(object):

    def test_instance(self):
        protocol = 'tcp'
        crypto_strategy = 'fernet'

        config = Configuration()
        config.cipher_suite = config.initialize_cipher_suite(crypto_strategy)

        subject = Ingress(protocol,
                          config.cipher_suite,
                          config.encryption_enabled)

        assert subject.__class__.__name__ == 'Ingress'
        assert subject.callback != None
        assert subject.QUEUE != None
        assert subject.queue == subject.QUEUE
        assert subject.cipher_suite == config.cipher_suite
        assert subject.encryption_enabled == config.encryption_enabled
