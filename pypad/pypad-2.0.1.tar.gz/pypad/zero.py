"""
Implementation of the zero-padding algorithm.
"""
import struct
from .exceptions import InvalidBlockSize, InvalidMessage

__all__ = ["pad", "unpad", "MAX_BLOCK_SIZE"]

MAX_BLOCK_SIZE = float("inf")

def pad(buf, block_size=0, byte=b"\x00"):
    """Padded with \x00 or byte until block_size."""
    if not isinstance(buf, bytes) or not isinstance(byte, bytes):
        raise TypeError("Buffer must be in bytes")

    if not len(byte) == 1:
        raise ValueError("Byte must be only one byte")

    if block_size == 0:
        return buf

    pad_size = block_size - (len(buf) % block_size)
    return buf + (byte * pad_size)

def unpad(buf, byte=None):
    """Truncate the padded bytes.
    None = autodetect
    """
    if not isinstance(buf, bytes):
        raise TypeError("Buffer must be in bytes")

    if byte is None:
        byte = buf[-1:]

    return buf.rstrip(byte)

