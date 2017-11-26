from iceman.configuration import Configuration
from iceman.traffic.egress import Egress

class TestInstance(object):

    def test_instance(self):
        protocol = 'tcp'
        queue = 0
        crypto_strategy = 'fernet'

        config = Configuration()
        config.cipher_suite = config.initialize_cipher_suite(crypto_strategy)

        subject = Egress(protocol,
                         queue,
                         config.cipher_suite,
                         config.encryption_enabled)

        assert subject.__class__.__name__ == 'Egress'
        assert subject.callback != None
        assert subject.queue == queue
        assert subject.cipher_suite == config.cipher_suite
        assert subject.encryption_enabled == config.encryption_enabled
