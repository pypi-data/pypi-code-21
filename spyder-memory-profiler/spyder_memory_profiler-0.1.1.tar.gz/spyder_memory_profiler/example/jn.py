# -*- coding: utf-8 -*-

@profile
def foo():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    del b
    return a

foo()