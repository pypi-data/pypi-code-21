#! /usr/bin/python3

#
# Copyright (c) 2015 Cisco Systems, Inc. and others.  All rights reserved.
#

import os, random, struct, hashlib, io, sys
from Crypto.Cipher import AES

__author__ = "paulq@cisco.com"
__copyright__ = "Copyright(c) 2015, Cisco Systems, Inc."
__version__ = "0.1"
__status__ = "alpha"


def decrypt_stream(key, iv, file_size, in_stream, chunksize=24*1024):

    """
    Decrypts a byte stream using AES (CBC mode) with the given key.
    A key is a string, 16, 24 or 32 bytes long. Longer keys are more secure.

    :param key: Encryption key
    :param in_stream: Byte stream like io.BytesIO
    :param chunksize: default chunk size
    :return: outstream
    """

    out_stream = io.BytesIO()

    # origsize = struct.unpack('<Q', in_stream.read(struct.calcsize('Q')))[0]
    # iv = in_stream.read(16)
    decryptor = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))

    # print("filesize=", origsize, " iv=", iv, "\n")

    while True:
        chunk = in_stream.read(chunksize)
        if len(chunk) == 0:
            break
        out_stream.write(decryptor.decrypt(chunk))
        print("chunk=", chunk, "\n")

    out_stream.truncate(file_size)
    return out_stream
