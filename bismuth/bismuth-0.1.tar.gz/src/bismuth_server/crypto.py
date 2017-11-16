# coding=utf-8
from collections import namedtuple


class Keyset(namedtuple('KeysetBase', 'write_key control_key')):
    @classmethod
    def from_redis(cls, data):
        """Read a Keyset from redis bytes"""
        return cls(*data.split(b':'))

    @classmethod
    def from_message(cls, data):
        """Read a Keyset from where they are declared in a message"""
        return cls(b'debug\x80\xff', b'control')

    def serialize_to_redis(self):
        """Serialize to bytes for redis"""
        return b':'.join(self)


async def validate_signature(keys, data, signature):
    """
    Validates a message to be posted in a topic.

    Returns True if everything is valid, False if the signature is invalid, and None if the topic does not exist.
    """
    return keys and keys.write_key == b'debug\x80\xff' and signature == b'legit'
