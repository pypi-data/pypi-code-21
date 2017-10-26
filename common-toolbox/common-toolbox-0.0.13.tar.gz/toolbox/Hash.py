#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午2:56
# @Author  : Hou Rong
# @Site    : 
# @File    : Hash.py
# @Software: PyCharm
import six
import json
import hashlib


def encode(string, hasher=hashlib.md5):
    return hasher(string.encode()).hexdigest()


def file_hash(file_or_path, hasher=hashlib.md5):
    if isinstance(file_or_path, six.string_types):
        file_obj = open(file_or_path, mode='rb')
    else:
        file_obj = file_or_path
    assert file_obj.mode == 'rb', 'Please use rb mode open the file'

    hasher_obj = hasher()
    for chunk in iter(lambda: file_obj.read(4096), b""):
        hasher_obj.update(chunk)
    return hasher_obj.hexdigest()


def get_token(d):
    """
    :type d: dict
    :return: str
    """
    return encode(json.dumps(d, sort_keys=True))
