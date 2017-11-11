from iceman.configuration import Configuration
from iceman.interceptor import Interceptor
from iceman.traffic.egress import Egress
from iceman.traffic.ingress import Ingress

def configuration():
    config = Configuration()
    strategy = config.CRYPTO_STRATEGIES[0]
    config.cipher_suite = config.initialize_cipher_suite(strategy)
    return config

def egress():
    queue = 0
    protocol = 'tcp'
    config = configuration()
    return Egress(protocol,
                  queue,
                  config.cipher_suite,
                  config.encryption_enabled)

def ingress():
    queue = 1
    protocol = 'tcp'
    config = configuration()
    return Ingress(protocol,
                   queue,
                   config.cipher_suite,
                   config.encryption_enabled)

class TestIntercept(object):
    def test_egress(self, mocker):
        traffic = egress()
        mocker.spy(Interceptor, 'intercept')
        mocker.patch('nfqueue.queue.try_run')
        Interceptor.intercept(traffic)
        assert Interceptor.intercept.call_count == 1

    def test_ingress(self, mocker):
        traffic = ingress()
        mocker.spy(Interceptor, 'intercept')
        mocker.patch('nfqueue.queue.try_run')
        Interceptor.intercept(traffic)

        assert Interceptor.intercept.call_count == 1
