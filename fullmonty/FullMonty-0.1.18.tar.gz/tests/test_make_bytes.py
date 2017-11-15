# coding=utf-8

"""
unit tests for make_bytes
"""
from io import BytesIO
from fullmonty.make_bytes import b

__docformat__ = 'restructuredtext en'
__author__ = 'wrighroy'


def test_str_write():
    """
    For python2: BytesIO.write(str)
    For python3: BytesIO.write(bytes)
    Use b(data) to convert a string to either str or bytes depending on python version
    """
    buf = BytesIO()
    data = 'foobar'
    buf.write(b(data))
    assert buf.getvalue().decode('utf-8') == data
