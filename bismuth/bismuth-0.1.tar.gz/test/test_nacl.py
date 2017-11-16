# coding=utf-8
import libnacl


def test_imported():
    assert libnacl.crypto_sign_BYTES > 0
