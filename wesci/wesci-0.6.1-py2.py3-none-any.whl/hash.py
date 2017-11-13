import hashlib


class Hash(object):

    HASH_ALGO = b'sha256'
    BASE64_HASH_VERSION = 'c2hhMjU2'

    @staticmethod
    def hash(data):
        return '%s:%s' % (hashlib.sha256(data).hexdigest(),
                          Hash.BASE64_HASH_VERSION)
