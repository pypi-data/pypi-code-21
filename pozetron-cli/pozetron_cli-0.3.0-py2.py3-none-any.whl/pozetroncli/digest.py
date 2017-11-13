"""
This module encapsulates logic related to Digest HTTP header.
"""

import base64
import hashlib


_HASHES = {
    'SHA-256': hashlib.sha256
}


class InvalidDigest(Exception):
    """This exception is raised if Digest has unknown/invalid format."""
    pass


def compare_digest(body, digest):
    """
    Computes body hash and compares it to digest.

    Returns True if digest match, False otherwise.
    Raises InvalidDigest if digest format is invalid/unknown.
    """
    try:
        # Digest example: 'SHA-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE='
        algorithm, hash = digest.split('=', 1)
        return _HASHES[algorithm](body).digest() == base64.b64decode(hash)
    except (KeyError, TypeError, ValueError):
        raise InvalidDigest('Invalid digest: {!r}'.format(digest))


def make_digest(body, algorithm='SHA-256'):
    return 'SHA-256=' + base64.b64encode(_HASHES[algorithm](body).digest()).decode('utf8')
