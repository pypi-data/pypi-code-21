# coding=utf-8
from hashlib import sha256, sha384, sha512

from bismuth_messages.proto.bismuth_message_pb2 import BismuthMessage, PublicMetaMessage
# noinspection PyProtectedMember
from bismuth_messages.proto.hash_type_pb2 import (
    HashType,
    SHA256,
    SHA384,
    SHA512,
)


__all__ = (
    'BismuthMessage',
    'PublicMetaMessage',
    'HashType',
)


HASH_MAPPING = {
    SHA256: sha256,
    SHA384: sha384,
    SHA512: sha512,
}


# patch message_id property onto BismuthMessage class
def message_id(self):
    try:
        hasher = HASH_MAPPING[self.hash_type]()
    except KeyError:
        raise ValueError('Invalid hash type')
    message_type_marker = bytes((self.has_metadata * 128 + self.hash_type,))
    hasher.update(self.topic)
    hasher.update(message_type_marker)
    hasher.update(self.data)
    return bytes((self.hash_type,)) + hasher.digest()

BismuthMessage.message_id = property(message_id)
