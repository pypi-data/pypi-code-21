# encoding: utf-8
"""
ex.py

Created by Hywel Thomas on 2011-07-28.
Copyright (c) 2011 Hywel Thomas. All rights reserved.
"""

import random

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'


def ex(a):
    """no comment!"""
    b = [random.randint(0,2**4-1) for _ in range((len(a)*4/2+1)*64)]
    ds = []
    for c in a:ds.extend([int(d,16) for d in hex(ord(c))[-2:]])
    for i in range(len(ds)):b[i*2+1] = (ds[i] + b[i*2]) % 16
    for i in range(len('%02x'%len(a))):b[len(b)-i*2-1] = int(('%02x'%len(a))[i],16)
    return ''.join([hex(d)[-1:] for d in b])

if __name__ == "__main__":
    print(ex(raw_input('Enter something>')))
