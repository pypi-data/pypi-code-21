import base64


class Crypter(object):
    def __init__(self):
        raise NotImplementedError

    def encode(self, text, key):
        raise NotImplementedError

    def decode(self, text, key):
        raise NotImplementedError

class SymmetricCrypter(Crypter):
    def __init__(self):
        pass

    def encode(self, text, key):
        enc = []
        for i in xrange(len(text)):
            key_c = key[i % len(key)]
            enc_c = chr((ord(text[i]) + ord(key_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode(''.join(enc))

    def decode(self, text, key):
        dec = []
        text = base64.urlsafe_b64decode(text)
        for i in xrange(len(text)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(text[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        return ''.join(dec)
