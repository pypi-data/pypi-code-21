#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Author: xingming
# Mail: huoxingming@gmail.com
# Created Time:  2015-12-11 01:23:50 AM
#############################################


def sum(*values):
    s = 0
    for v in values:
        i = int(v)
        s = s + i
    print s

def output():
    print 'this is a test hello .'
