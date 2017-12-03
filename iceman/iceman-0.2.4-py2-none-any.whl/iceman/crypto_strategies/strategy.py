# -*- coding: utf-8 -*-
"""strategy module
"""
class Strategy(object):
    """Abstracted Strategy class
    """

    def encrypt(self, payload):
        """encrypt interface
        """
        raise NotImplementedError()

    def decrypt(self, token):
        """decrypt interface
        """
        raise NotImplementedError()
