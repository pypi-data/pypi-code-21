'''pastry_rsa provides a signing method that works with openssl rsautl'''

import rsa


def sign(message, raw_key):
    '''sign a request the same way openssl rsautl would'''
    priv_key = rsa.PrivateKey.load_pkcs1(raw_key)
    keylength = rsa.common.byte_size(priv_key.n)
    padded = rsa.pkcs1._pad_for_signing(message, keylength)
    payload = rsa.transform.bytes2int(padded)
    encrypted = rsa.core.encrypt_int(payload, priv_key.d, priv_key.n)
    return rsa.transform.int2bytes(encrypted, keylength)
