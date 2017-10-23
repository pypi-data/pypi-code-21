#!/usr/bin/python
# -*- coding: utf-8 -*-

import io
import zlib
import base64
import binascii
import numpy as np


class CompressError(Exception):
    pass


def compress(s, text=True):
    s = zlib.compress(s.encode(), 9)
    if text:
        s = base64.b64encode(s).decode()
    return s


def compressFile(f, text=True):
    try:
        return compress(open(f).read(), text)
    except IOError:
        return ''


def decompress(bts, text=True):
    try:
        if text:
            bts = base64.b64decode(bts)
        return zlib.decompress(bts)
    except (binascii.Error, zlib.error):
        raise CompressError('The string does not seem to be compressed')


def compressNumpyArray(array, text=True):
    buf = io.BytesIO()
    # noinspection PyTypeChecker
    np.savez_compressed(buf, array)
    bts = buf.getvalue()
    if text:
        bts = base64.b64encode(bts).decode()
    return bts


def decompressNumpyArray(array, text=True):
    try:
        if text:
            array = base64.b64decode(array)
        return np.load(io.BytesIO(array))['arr_0']
    except (TypeError, OSError, binascii.Error):
        return None
