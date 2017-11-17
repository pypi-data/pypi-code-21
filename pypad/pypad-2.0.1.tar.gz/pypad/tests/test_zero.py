"""
Unit tests for the Zero padding algorithm
"""

from pypad import zero
import pytest

def test_zero_sample():
    """Testing the Zero implementation with some generic test data"""
    original = b"Testing"
    expected = b"Testing\x00\x00\x00"
    block_sz = 10

    padded = zero.pad(original, block_sz)
    assert padded == expected

    unpadded = zero.unpad(padded)
    assert unpadded == original

def test_zero_sample_nonzero():
    """Testing the Zero implementation with some generic test data"""
    original = b"Testing"
    expected = b"Testing\x77\x77\x77"
    block_sz = 10
    pad_byte = b"\x77"

    padded = zero.pad(original, block_sz, pad_byte)
    assert padded == expected

    unpadded = zero.unpad(padded)
    assert unpadded == original

def test_zero_empty():
    """Testing the Zero with an empty buffer with a small block size"""
    original = b""
    expected = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    block_sz = 10

    padded = zero.pad(original, block_sz)
    assert padded == expected

    unpadded = zero.unpad(padded)
    assert unpadded == original

def test_zero_invalid_byte():
    """Testing the Zero padding algorithm with an invalid byte value"""
    original = b"Testing"
    with pytest.raises(ValueError):
        zero.pad(original, byte=b"meme")

def test_zero_unequal_original():
    """Testing the Zero with an invalid message"""
    original = b"Testing\x00"
    expected = b"Testing\x00\x00\x00"
    block_sz = 10

    padded = zero.pad(original, block_sz)
    assert padded == expected

    unpadded = zero.unpad(padded)
    assert unpadded != original

def test_zero_invalid_type():
    """Testing the Zero with an invalid message type"""
    bad_msg = ['T', 'e', 's', 't', 'i', 'n', 'g']
    with pytest.raises(TypeError):
        zero.pad(bad_msg)
