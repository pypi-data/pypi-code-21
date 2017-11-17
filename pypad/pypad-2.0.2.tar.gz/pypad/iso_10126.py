"""
Implementation of the ISO 10126 algorithm.
"""
import struct
from .utils import random_bytes
from .exceptions import InvalidBlockSize, InvalidMessage

__all__ = ["pad", "unpad", "MAX_BLOCK_SIZE"]

MAX_BLOCK_SIZE = 0x100


def pad(buf, block_size=MAX_BLOCK_SIZE):
    """Padded with random bytes followed by the number of bytes padded."""
    if not isinstance(buf, bytes):
        raise TypeError("Buffer must be in bytes")

    if block_size > MAX_BLOCK_SIZE:
        raise InvalidBlockSize("Maximum block size for ISO 10126 is {}".format(MAX_BLOCK_SIZE))

    pad_size = block_size - (len(buf) % block_size)
    return buf + random_bytes(pad_size - 1) + struct.pack("B", pad_size & 0xff)


def unpad(buf):
    """Extract the last byte and truncate the padded bytes"""
    if not isinstance(buf, bytes):
        raise TypeError("Buffer must be in bytes")

    bufsize = len(buf)
    if bufsize == 0:
        raise InvalidMessage("The buffer cannot be empty")

    pad_size = ord(buf[-1:])
    pad_size = pad_size or MAX_BLOCK_SIZE

    if bufsize < pad_size:
        raise InvalidMessage("The buffer does not match the pad length.")

    return buf[:-pad_size]
