"""
Unit tests for the PKCS#7 padding algorithm
"""

from pypad import pkcs7
from pypad.exceptions import InvalidBlockSize, InvalidMessage
import pytest

def test_pkcs7_sample():
    """Testing the PKCS#7 implementation with some generic test data"""
    original = b"Testing"
    expected = b"Testing\x03\x03\x03"
    block_sz = 10

    padded = pkcs7.pad(original, block_sz)
    assert padded == expected

    unpadded = pkcs7.unpad(padded)
    assert unpadded == original

def test_pkcs7_aligned():
    """Testing the PKCS#7 implementation with aligned data"""
    original = b"Testing"
    expected = b"Testing\x07\x07\x07\x07\x07\x07\x07"
    block_sz = 7

    padded = pkcs7.pad(original, block_sz)
    assert padded == expected

    unpadded = pkcs7.unpad(padded)
    assert unpadded == original

def test_pkcs7_empty():
    """Testing the PKCS#7 with an empty buffer with a small block size"""
    original = b""
    expected = b"\x0a\x0a\x0a\x0a\x0a\x0a\x0a\x0a\x0a\x0a"
    block_sz = 10

    padded = pkcs7.pad(original, block_sz)
    assert padded == expected

    unpadded = pkcs7.unpad(padded)
    assert unpadded == original

def test_pkcs7_empty_max():
    """Testing the PKCS#7 with an empty buffer with the maximum block size"""
    original = b""
    expected = b"\x00" * pkcs7.MAX_BLOCK_SIZE

    padded = pkcs7.pad(original)
    assert padded == expected

    unpadded = pkcs7.unpad(padded)
    assert unpadded == original

def test_pkcs7_invalid_block_size():
    """Testing the PKCS#7 with an invalid block size"""
    original = b"Testing"
    block_sz = pkcs7.MAX_BLOCK_SIZE + 1
    with pytest.raises(InvalidBlockSize):
        pkcs7.pad(original, block_sz)

def test_pkcs7_invalid_message():
    """Testing the PKCS#7 with an invalid message"""
    bad_msg = b"Testing\x04\x04\x04"
    with pytest.raises(InvalidMessage):
        pkcs7.unpad(bad_msg)

    bad_msg = b"Testing\x04\x04\x03\x04"
    with pytest.raises(InvalidMessage):
        pkcs7.unpad(bad_msg)

def test_pkcs7_invalid_type():
    """Testing the PKCS#7 with an invalid message type"""
    bad_msg = ['T', 'e', 's', 't', 'i', 'n', 'g']
    with pytest.raises(TypeError):
        pkcs7.pad(bad_msg)
