# -*- coding: utf-8 -*-
"""configuration module
"""
import os
import importlib
import ConfigParser

from iceman.traffic.egress import Egress
from iceman.traffic.ingress import Ingress

class Configuration(object):
    """Configuration class - loads runtime variables
    """

    NAMESPACE = 'interceptor'
    CRYPTO_STRATEGIES = [
        'fernet',
        'icemicro',
    ]
    PROTOCOLS = [
        'tcp',
        'udp'
    ]
    QUEUES = {
        'egress': Egress.QUEUE,
        'ingress': Ingress.QUEUE
    }

    def __init__(self):
        self.settings = Configuration.get_settings()
        self.encryption_enabled = self.get_encryption_enabled()

    @classmethod
    def get_settings(cls):
        """loads configuration settings from disk
        """

        settings_file = os.path.join(os.path.dirname(__file__), 'interceptor.cfg')
        parser = ConfigParser.ConfigParser(os.environ)
        parser.read(settings_file)
        return parser

    def initialize_cipher_suite(self, crypto_strategy):
        """using configuration settings and given a crypto_strategy, initializes the cipher suite

        :param crypto_strategy: cipher implementation (e.g., fernet)
        :type crypto_strategy: str

        :returns instance -- the cipher suite defined by the crypto strategy
        """
        module = importlib.import_module("iceman.crypto_strategies.{}".format(crypto_strategy))
        klass = crypto_strategy.capitalize()

        if not 'ICEMAN_PRESHARED_KEY' in os.environ:
            exit('ERROR: ICEMAN_PRESHARED_KEY env varirable not set')

        preshared_key = self.settings.get(self.NAMESPACE, 'preshared_key')
        cipher_suite = getattr(module, klass)(preshared_key)
        return cipher_suite

    def get_encryption_enabled(self):
        """returns the encryption_enabled flag

        :returns bool -- the encryption_enabled flag
        """
        if not 'ICEMAN_ENCRYPTION_ENABLED' in os.environ:
            exit('ERROR: ICEMAN_ENCRYPTION_ENABLED env varirable not set')

        is_enabled = self.settings.get(self.NAMESPACE, 'encryption_enabled').lower() == 'true'
        return is_enabled
