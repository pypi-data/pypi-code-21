import zmq

# zprocess.encrypt format-1.0 [encrypted]
# {'master_key': 'PBKDF2(HMACSHA256, password, salt, 2**kdf_strength)',
#  'encryption_key': 'HMACSHA256(master_key, encryption_nonce)',
#  'hmac_key': 'HMACSHA256(master_key, hmac_nonce)',
#  'ciphertext': 'AES256CFB(encryption_key, iv, plaintext)',
#  'mac': 'HMACSHA256(hmac_key, ciphertext)',
#  'framing': 'ZPEF[1:ver_major][1:ver_minor][8:salt][1:kdf_strength][8:hmac_nonce][8:encryption_nonce][16:iv][ciphertext][32:mac]'}

# zprocess.encrypt format-1.0 [authenticated]
# {'salt': '0xdeadbeef',
#  'hmac_nonce': 0xdeadbeef,
#  'kdf_niter': 1000
#  'master_key': 'PBKDF2(HMACSHA256, password, salt, kdf_niter)',
#  'hmac_key': 'HMACSHA256(master_key, hmac_nonce)',
#  'mac': 'HMACSHA256(hmac_key, ciphertext)',
#  'framing': '[header] [null] [hmac_nonce][plaintext] [mac]'}

# def encrypt(password):
#     check cache for password -> master_key, salt
#     if not there:
#         generate salt
#         derive key
#         save in cache
#     generate hmac nonce
#     generate encryption nonce

# def decrypt(password):


from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class ZProcessEncryption(object):

    """Class for symmetric, authenticated encryption with a preshared
    password. Version 0.1. Message format for version 0.1 is:

    ZPEF[1:ver_major][1:ver_minor][1:kdf_strength][8:salt]
    [8:hmac_nonce][8:encryption_nonce][16:iv][ciphertext][32:mac]

    where the numbers before the colons indicate the number of bytes (and
    newlines are meaningless). 'ZPEF' at the start are the ASCII bytes for
    'ZPEF'. No numerical quantity is more than a byte (the nonces are to be
    treated as bytestrings, not long integers), so we do not define
    endianness. kdf_strength is log2 of the number of iterations of the hash
    for the key derivation funcion, so kdf_strength = 20 means 2**20 = 1048576
    iterations.

    Version 0.1 uses AES 256 in CFB mode for encryption, HMACSHA256 for
    message authentication, PBKDF2HMAC with SHA256 and a 256 bit random salt
    for the master key derivation, with 2**20 iterations by default. The
    encryption and authentication keys are derived separately from the master
    key using HMAC-SHA256 and separate 256 bit randomly generated nonces.

    Only the iv + ciphertext is hashed for message authentication.

    Once a master key has been derived from a (randomly generated) salt, the
    same master key will be used for that password for the lifetime of this
    object, but different encryption and authentication keys will result from
    the unique nonces each time a message is encrypted. Thus repeated messages
    should be sent from the same object so that a new master key need not be
    derived each time a message is sent, as it is desirable for this to be
    somewhat costly by setting kdf_strength to as high a number as is
    tolerable for performance.

    The only information this scheme ought to leak if implemented correctly is
    the size of the message."""

    VERSION_MAJOR = 0
    VERSION_MINOR = 1

    # KDF:
    SALT_SIZE = 256//8
    KDF = PBKDF2HMAC
    KDF_HASH = hashes.SHA256
    KDF_STRENGTH = 16

    KEYSIZE = 256//8
    
    def __init__(self):
        self.keys = {}

    def encrypt(self, plaintext, password, kdf_strength=None):
        if kdf_strength is None:
            kdf_strength = self.KDF_STRENGTH
        try:
            key, salt = self.keys[password]
        except KeyError:
            salt = os.urandom(self.SALT_SIZE)
            kdf = self.KDF(self.KDF_HASH(), length=self.KEYSIZE, salt=salt,
                           iterations=2**kdf_strength, backend=default_backend())
            import time
            start_time = time.time()
            key = kdf.derive(password)
            print(time.time() - start_time)

    def decrypt(self, message):
        pass

encryption = ZProcessEncryption()
encryption.encrypt(b'hello', b'password')

# class EncryptingSocket(zmq.Socket):
#     def send(self, *args, **kwargs):
#         print('send', args, kwargs)
#         return zmq.Socket.send(self, *args, **kwargs)

#     def recv(self, *args, **kwargs):
#         print('recv', args, kwargs)
#         return zmq.Socket.recv(self, *args, **kwargs)

# class EncryptingContext(zmq.Context):
#     _socket_class = EncryptingSocket


# ctx = EncryptingContext()
# sock1 = ctx.socket(zmq.REQ)
# sock2 = ctx.socket(zmq.REP)

# port = sock2.bind_to_random_port('tcp://*')
# sock1.connect('tcp://localhost:%d'%port)

# sock1.send(b'test')
# print(sock2.recv())