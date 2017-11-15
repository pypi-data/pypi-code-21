"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.brewer.brewer import Brewer
from pubkeeper.utils.crypto import PubCrypto
from Crypto import Random
from Crypto.Cipher import AES
from binascii import hexlify, unhexlify
from uuid import uuid4


class ProtocolBrewer(Brewer):
    def __init__(self, *args, brewer_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.brewer_id = brewer_id or uuid4().hex
        self.brewing = {}
        self.brews = []

        self._crypto = None
        if self.crypto:
            self._crypto = {
                'mode': AES.MODE_CBC,
                'key': hexlify(Random.new().read(16)).decode()
            }
            self._cipher = PubCrypto(
                self._crypto['mode'],
                False
            )

    def get_config(self):
        ret = {}

        if self.crypto:
            ret['cipher'] = self._crypto

        return ret

    def new_patrons(self, patrons):
        with self.topic_lock:
            for patron in patrons:
                brew = self.get_brew(patron['brew']['name'])

                if brew is None:
                    raise RuntimeError("Brewer could not match a parity "
                                       "brew for patron brew: {}".format(
                                           patron['brew']
                                       ))

                if patron['patron_id'] in self.brewing:
                    self.remove_patron(patron['patron_id'])

                if brew not in self.brewing:
                    self.brewing[brew] = {
                        patron['patron_id']: patron['brew']
                    }
                else:
                    self.brewing[brew][patron['patron_id']] = patron['brew']

            for patron in patrons:
                brew.start_brewer(self.brewer_id,
                                  self.topic,
                                  patron['patron_id'],
                                  patron['brew'])

                self.logger.info("Started brewer for {}:{}".format(
                    self.topic, patron['patron_id']
                ))

    def remove_patron(self, patron_id):
        with self.topic_lock:
            for brew, patrons in self.brewing.copy().items():
                if patron_id in patrons:
                    brew.stop_brewer(self.brewer_id,
                                     self.topic,
                                     patron_id)

                    del(self.brewing[brew][patron_id])

                if len(self.brewing[brew]) == 0:
                    del(self.brewing[brew])

                self.logger.info("Stopped brewer for {}:{}".format(
                    self.topic, patron_id
                ))

    def brew(self, data):
        if self.crypto:
            data = self._cipher.encrypt(
                unhexlify(self._crypto['key']),
                data
            )

        with self.topic_lock:
            for brew, patrons in self.brewing.items():
                brew.brew(self.brewer_id,
                          self.topic,
                          data,
                          patrons)
