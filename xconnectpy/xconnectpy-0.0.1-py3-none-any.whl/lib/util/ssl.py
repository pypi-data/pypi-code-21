#!/usr/bin/python

import ssl


class SSL:

    def __init__(self, ssl_tunnel=True, certificates='certificates/xconnect_certificates.pem'):
        self.ssl_tunnel = ssl_tunnel
        self.certificates = certificates

    def context(self):
        return self.create_context(self.ssl_tunnel, self.certificates)

    def create_context(self, ssl_tunnel=False, certificates='certificates/xconnect_certificates.pem') -> object:
        self.__init__(ssl_tunnel, certificates)

        if ssl_tunnel:
            if certificates:
                ctx = ssl._create_unverified_context(certfile=certificates)
            else:
                ctx = ssl._create_unverified_context()

            return ctx
        else:
            return None
