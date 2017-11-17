"""
Unit tests for the ISO 10126 padding algorithm
"""

from pypad import iso_10126
from pypad.exceptions import InvalidBlockSize, InvalidMessage
import pytest


def test_iso_10126_sample():
    """Testing the ISO 10126 implementation with some generic test data"""
    original = b"Testing"
    expected = b"Testing", b"\x03"
    block_sz = 10

    padded = iso_10126.pad(original, block_sz)
    assert padded.startswith(expected[0]) and padded.endswith(expected[1])

    unpadded = iso_10126.unpad(padded)
    assert unpadded == original


def test_iso_10126_aligned():
    """Testing the ISO 10126 implementation with aligned data"""
    original = b"Testing"
    expected = b"Testing", b"\x07"
    block_sz = 7

    padded = iso_10126.pad(original, block_sz)
    assert padded.startswith(expected[0]) and padded.endswith(expected[1])

    unpadded = iso_10126.unpad(padded)
    assert unpadded == original


def test_iso_10126_empty():
    """Testing the ISO 10126 with an empty buffer with a small block size"""
    original = b""
    expected = b"", b"\x0a"
    block_sz = 10

    padded = iso_10126.pad(original, block_sz)
    assert padded.startswith(expected[0]) and padded.endswith(expected[1])

    unpadded = iso_10126.unpad(padded)
    assert unpadded == original


def test_iso_10126_empty_max():
    """Testing the ISO 10126 with an empty buffer with the maximum block size"""
    original = b""
    expected = b"\x00"

    padded = iso_10126.pad(original)
    assert padded.endswith(expected)

    unpadded = iso_10126.unpad(padded)
    assert unpadded == original


def test_iso_10126_invalid_block_size():
    """Testing the ISO 10126 with an invalid block size"""
    original = b"Testing"
    block_sz = iso_10126.MAX_BLOCK_SIZE + 1
    with pytest.raises(InvalidBlockSize):
        iso_10126.pad(original, block_sz)


def test_iso_10126_invalid_message():
    """Testing the ISO 10126 with an invalid message"""
    bad_msg = b"Testing\x09"
    with pytest.raises(InvalidMessage):
        iso_10126.unpad(bad_msg)


def test_iso_10126_invalid_type():
    """Testing the ISO 10126 with an invalid message type"""
    bad_msg = ['T', 'e', 's', 't', 'i', 'n', 'g']
    with pytest.raises(TypeError):
        iso_10126.pad(bad_msg)
