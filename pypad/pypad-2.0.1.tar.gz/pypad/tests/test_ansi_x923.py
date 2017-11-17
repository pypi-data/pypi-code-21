"""
Unit tests for the ANSI x.923 padding algorithm
"""

from pypad import ansi_x923
from pypad.exceptions import InvalidBlockSize, InvalidMessage
import pytest

def test_ansi_x923_sample():
    """Testing the ANSI x.923 implementation with some generic test data"""
    original = b"Testing"
    expected = b"Testing\x00\x00\x03"
    block_sz = 10

    padded = ansi_x923.pad(original, block_sz)
    assert padded == expected

    unpadded = ansi_x923.unpad(padded)
    assert unpadded == original

def test_ansi_x923_aligned():
    """Testing the ANSI x.923 implementation with aligned data"""
    original = b"Testing"
    expected = b"Testing\x00\x00\x00\x00\x00\x00\x07"
    block_sz = 7

    padded = ansi_x923.pad(original, block_sz)
    assert padded == expected

    unpadded = ansi_x923.unpad(padded)
    assert unpadded == original

def test_ansi_x923_empty():
    """Testing the ANSI x.923 with an empty buffer with a small block size"""
    original = b""
    expected = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0a"
    block_sz = 10

    padded = ansi_x923.pad(original, block_sz)
    assert padded == expected

    unpadded = ansi_x923.unpad(padded)
    assert unpadded == original

def test_ansi_x923_empty_max():
    """Testing the ANSI x.923 with an empty buffer with the maximum block size"""
    original = b""
    expected = b"\x00" * ansi_x923.MAX_BLOCK_SIZE

    padded = ansi_x923.pad(original)
    assert padded == expected

    unpadded = ansi_x923.unpad(padded)
    assert unpadded == original

def test_ansi_x923_invalid_block_size():
    """Testing the ANSI x.923 with an invalid block size"""
    original = b"Testing"
    block_sz = ansi_x923.MAX_BLOCK_SIZE + 1
    with pytest.raises(InvalidBlockSize):
        ansi_x923.pad(original, block_sz)

def test_ansi_x923_invalid_message():
    """Testing the ANSI x.923 with an invalid message"""
    bad_msg = b"Testing\x00\x00\x04"
    with pytest.raises(InvalidMessage):
        ansi_x923.unpad(bad_msg)

    bad_msg = b"Testing\x09"
    with pytest.raises(InvalidMessage):
        ansi_x923.unpad(bad_msg)

def test_ansi_x923_invalid_type():
    """Testing the ANSI x.923 with an invalid message type"""
    bad_msg = ['T', 'e', 's', 't', 'i', 'n', 'g']
    with pytest.raises(TypeError):
        ansi_x923.pad(bad_msg)
