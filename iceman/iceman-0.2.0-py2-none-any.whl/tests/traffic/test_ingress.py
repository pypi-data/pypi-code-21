from iceman.configuration import Configuration
from iceman.traffic.ingress import Ingress

class TestInstance(object):

    def test_instance(self):
        queue = 0
        protocol = 'tcp'
        crypto_strategy = 'fernet'

        config = Configuration()
        config.cipher_suite = config.initialize_cipher_suite(crypto_strategy)

        subject = Ingress(protocol,
                          queue,
                          config.cipher_suite,
                          config.encryption_enabled)

        assert subject.__class__.__name__ == 'Ingress'
        assert subject.callback != None
        assert subject.queue == queue
        assert subject.cipher_suite == config.cipher_suite
        assert subject.encryption_enabled == config.encryption_enabled
