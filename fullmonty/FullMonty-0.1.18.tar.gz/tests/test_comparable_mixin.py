# coding=utf-8

"""
Describe Me!
"""
from fullmonty.comparable_mixin import ComparableMixin

__docformat__ = 'restructuredtext en'
__author__ = 'wrighroy'


# noinspection PyDocstring
class BaseClass(object):
    pass


# noinspection PyDocstring
def test_int_compare():
    # noinspection PyDocstring
    def cmpkey(self):
        return self.data

    Aclass = type('Aclass', (BaseClass, ComparableMixin), {'_cmpkey': cmpkey})
    a1 = Aclass()
    a2 = Aclass()
    a1.data = 1
    a2.data = 1
    assert a1 == a2
    assert a1 <= a2

    a2.data = 2
    assert a1 != a2
    assert a1 < a2
    assert a1 <= a2

    a1.data = 2
    assert a1 == a2
    assert a1 >= a2

    a1.data = 3
    assert a1 > a2
    assert a1 >= a2


# noinspection PyDocstring
def test_str_compare():
    # noinspection PyDocstring
    def cmpkey(self):
        return self.data

    Aclass = type('Aclass', (BaseClass, ComparableMixin), {'_cmpkey': cmpkey})
    a1 = Aclass()
    a2 = Aclass()
    a1.data = '1'
    a2.data = '1'
    assert a1 == a2
    assert a1 <= a2

    a2.data = '2'
    assert a1 != a2
    assert a1 < a2
    assert a1 <= a2

    a1.data = '2'
    assert a1 == a2
    assert a1 >= a2

    a1.data = '3'
    assert a1 > a2
    assert a1 >= a2
