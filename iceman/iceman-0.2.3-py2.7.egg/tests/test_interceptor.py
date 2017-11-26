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
