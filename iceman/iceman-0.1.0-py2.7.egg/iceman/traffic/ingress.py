# -*- coding: utf-8 -*-
"""iceman/Traffic/ingress.py
"""
from iceman.traffic.traffic import Traffic

class Ingress(Traffic):
    """Ingress Traffic implementation

    Attributes:
        QUEUE (int): nfqueue number

    :param protocol: tcp or udp
    :type cipher_suite: str

    :param cipher_suite: crypto wrapper cipher strategy
    :type cipher_suite: instance

    :param encryption_enabled: encryption flag
    :type encryption_enabled: bool
    """

    QUEUE = 1

    def __init__(self, protocol, cipher_suite, encryption_enabled):
        super(Ingress, self).__init__(protocol,
                                      self.QUEUE,
                                      cipher_suite,
                                      encryption_enabled)

    def callback(self, not_used, payload): #pylint: disable=unused-argument
        """nfqueue callback
        """
        self.transform('decrypt', payload)
