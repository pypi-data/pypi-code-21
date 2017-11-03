#!/usr/bin/env python
# encoding: utf-8
"""
edx.py

Created by Hywel Thomas on 2011-07-28.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'


def dx(e):
    """no comment!"""
    if len(e)%2**6!=0:return e
    dph = [hex(int(e[i+1],2**4)-int(e[i],2**4)+2**16 if int(e[i+1],2**4)-int(e[i],2**4)<1 else int(e[i+1],2**4)-int(e[i],2**4))[-1:] for i in range(0,len(e),2)]
    exec('d="{x}"'.format(x=''.join([chr(int(dph[i]+dph[i+1],2**4)) for i in range(0,len(dph),2)][:int(e[-1]+e[-3],2**4)])))
    return d

if __name__ == "__main__":
    print(dx(raw_input('Enter something>')))

