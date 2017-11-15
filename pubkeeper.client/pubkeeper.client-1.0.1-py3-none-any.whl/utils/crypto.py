"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from Crypto.Cipher import AES
from Crypto import Random
from binascii import hexlify, unhexlify, Error


class PubCrypto:
    BS = AES.block_size

    def __init__(self, mode, binary=True):
        self.mode = mode
        self.binary = binary

    def pad(self, s):
        return s + ((self.BS - len(s) % self.BS) *
                    chr(self.BS - len(s) % self.BS)).encode()

    def unpad(self, s):
        return s[0:-(s[-1])]

    def encrypt(self, key, raw):
        raw = self.pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, self.mode, iv)
        crypted = cipher.encrypt(raw)
        if self.binary:
            return iv + crypted
        else:
            return hexlify(iv + crypted)

    def decrypt(self, key, enc):
        try:
            if not self.binary:
                enc = unhexlify(enc)
            iv = enc[:16]
            enc = enc[16:]
            cipher = AES.new(key, self.mode, iv)
            return self.unpad(cipher.decrypt(enc))
        except Error:
            raise RuntimeError("Unable to unhex encrypted data")
