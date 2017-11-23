#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import hashlib


def hash_data(data):
    """
    Fingerprint of the data.
    """
    m = hashlib.md5()
    m.update(pickle.dumps(data))
    return m.hexdigest()
