import nfqueue

from iceman.configuration import Configuration
from iceman.traffic.traffic import Traffic

def configuration():
    config = Configuration()
    config.cipher_suite = config.initialize_cipher_suite('fernet')
    return config


class TestInstance(object):
    def test_instance(self):
        protocol = 'tcp'
        queue = 9001
        config = configuration()

        subject = Traffic(protocol,
                          queue,
                          config.cipher_suite,
                          config.encryption_enabled)
        assert subject.__class__.__name__ == 'Traffic'
        assert subject.queue == queue

class TestTransform(object):
    def test_transform(self, mocker):

        # mocker.patch('nfqueue.queue.set_verdict_modified')

        protocol = 'tcp'
        queue = 9001
        config = configuration()

        subject = Traffic(protocol,
                          queue,
                          config.cipher_suite,
                          config.encryption_enabled)
        # mocker.patch('nfqueue.set_verdict_modified')
        # obj.ingress()
        # assert Interceptor.intercept.call_count == 1

