"""
passalt: Generate and check password hash.
"""

from os import urandom
from hashlib import sha512


def new(passwd):
    """New a salted hash string"""
    salt = urandom(16)
    hasher = sha512()
    hasher.update(salt)
    hasher.update(passwd.encode())
    return 'sha512${}${}'.format(salt.hex(), hasher.hexdigest())


def check(hashstr, passwd):
    """Check if passwd valid"""
    try:
        _, saltstr, hashed_passwd = hashstr.split('$')
    except:
        raise RuntimeError('not a valid hash string')
    hasher = sha512()
    hasher.update(bytearray.fromhex(saltstr))
    hasher.update(passwd.encode())
    return hasher.hexdigest() == hashed_passwd
