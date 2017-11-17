"""
Implementation of the ANSI x.923 algorithm.
"""
import struct
from .exceptions import InvalidBlockSize, InvalidMessage

__all__ = ["pad", "unpad", "MAX_BLOCK_SIZE"]

MAX_BLOCK_SIZE = 0x100

def pad(buf, block_size=MAX_BLOCK_SIZE):
    """Padded with \x00 followed by the number of bytes padded."""
    if not isinstance(buf, bytes):
        raise TypeError("Buffer must be in bytes")

    if block_size > MAX_BLOCK_SIZE:
        raise InvalidBlockSize("Maximum block size for ANSI x.923 is {}".format(MAX_BLOCK_SIZE))

    pad_size = block_size - (len(buf) % block_size)
    return buf + (b"\x00" * (pad_size - 1)) + struct.pack("B", pad_size & 0xff)

def unpad(buf):
    """Extract the last byte and truncate the padded \x00's"""
    if not isinstance(buf, bytes):
        raise TypeError("Buffer must be in bytes")

    bufsize = len(buf)
    if bufsize == 0:
        raise InvalidMessage("The buffer cannot be empty")

    pad_size = ord(buf[-1:])
    pad_size = pad_size or MAX_BLOCK_SIZE

    if bufsize < pad_size:
        raise InvalidMessage("The buffer does not match the pad length.")

    padding = buf[bufsize - pad_size:-1]
    if not all(b in (0, b'\x00') for b in padding):
        raise InvalidMessage("The buffer was not padded with ANSI x.923")

    return buf[:-pad_size]
