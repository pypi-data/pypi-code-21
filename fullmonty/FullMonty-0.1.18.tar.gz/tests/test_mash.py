# coding=utf-8

"""
Test Mash
"""
import unittest
from argparse import Namespace

from fullmonty.mash import Mash
from fullmonty.simple_logger import info

__docformat__ = 'restructuredtext en'
__author__ = 'wrighroy'


# noinspection PyMethodMayBeStatic
class TestMash(unittest.TestCase):
    """
    Test the Mash class
    """

    def test_basic_dict(self):
        """
        basic functionality
        """
        a = Mash()
        assert len(a) == 0
        a['foo'] = 'bar'
        assert len(a) == 1
        assert a['foo'] == 'bar'
        assert a.foo == 'bar'
        a['foo'] = 'fig'
        assert len(a) == 1
        assert a['foo'] == 'fig'
        assert a.foo == 'fig'
        del a['foo']
        assert len(a) == 0

    def test_basic_namespace(self):
        """
        basic functionality
        """
        a = Mash()
        assert len(a) == 0
        a.foo = 'bar'
        assert len(a) == 1
        assert a['foo'] == 'bar'
        assert a.foo == 'bar'
        a.foo = 'fig'
        assert len(a) == 1
        assert a['foo'] == 'fig'
        assert a.foo == 'fig'
        del a.foo
        assert len(a) == 0

    def test_identitiy(self):
        """
        test identity
        """
        a = Mash()
        a.foo = 'bar'
        assert a['foo'] == a.foo
        assert a.foo == a['foo']

    def test_keys(self):
        """
        test dict.keys
        """
        a = Mash()
        a.foo = 1
        a.bar = 2
        a.fig = 3
        assert len(a) == 3
        assert len(a.keys()) == 3
        assert set(a.keys()) == {'foo', 'bar', 'fig'}

    def test_copy_constructor(self):
        """
        test copy constructor
        """
        a = Mash()
        a.foo = 1
        a.bar = 2
        a.fig = 3
        b = Mash(a)
        assert len(b) == 3
        assert len(b.keys()) == 3
        assert set(b.keys()) == {'foo', 'bar', 'fig'}

    def test_delattr(self):
        """
        test delattr
        """
        a = Mash()
        a.foo = 1
        a.bar = 2
        a.fig = 3
        assert set(a.keys()) == {'foo', 'bar', 'fig'}
        delattr(a, 'bar')
        assert set(a.keys()) == {'foo', 'fig'}

    def test_invalid_attribute_name_keys(self):
        """
        These keys are accessible only via dict accessors.  You can not use attribute accessors.
        :return:
        :rtype:
        """
        a = Mash()
        a[1] = 'foo'
        a['a*b'] = 'bar'
        a['c.d'] = 'fig'
        assert a[1] == 'foo'
        assert a['a*b'] == 'bar'
        assert a['c.d'] == 'fig'

    def test_constructors(self):
        data = {'e': 5, 'f': 6}
        namespace = Namespace(**data)

        assert Mash(data)
        assert Mash(namespace)
        self.assertDictEqual(Mash(data), data)
        self.assertDictEqual(Mash(namespace), data)

    def test_eq(self):
        data = {'a': 1, 'b': 2}
        namespace = Namespace(**data)
        mash = Mash(namespace)
        mash2 = Mash(data)
        # info("data: " + repr(data))
        # info("mash: " + repr(mash))
        # info("mash2: " + repr(mash2))
        self.assertDictEqual(mash, data, "mash.__dict__ == data")
        self.assertEqual(mash, mash2, "mash.__eq__(mash2)")
        self.assertDictEqual(mash, namespace.__dict__, "mash.__dict__ == namespace.__dict__")

    def test_comparisons(self):
        data = {'c': 3, 'd': 4}
        namespace = Namespace(**data)

        # mash(data) vs data
        self.assertDictEqual(data, Mash(data))
        self.assertDictEqual(Mash(data), data)

        # mash(namespace) vs namespace
        self.assertDictEqual(Mash(namespace), namespace.__dict__)
        self.assertDictEqual(namespace.__dict__, Mash(namespace))

        # mash(namespace) vs data
        self.assertDictEqual(Mash(namespace), data)
        self.assertDictEqual(data, Mash(namespace))

        # mash(data) vs namespace
        self.assertDictEqual(Mash(data), namespace.__dict__)
        self.assertDictEqual(namespace.__dict__, Mash(data))

    def test_vars(self):
        a = Mash()
        # a[1] = 'foo'
        a['a*b'] = 'bar'
        a['c.d'] = 'fig'
        b = Namespace(**a)

        assert getattr(a, 'a*b', None)
        assert getattr(b, 'a*b', None)
        assert getattr(a, 'c.d', None)
        assert getattr(b, 'c.d', None)

        assert b
        # assert b[1] == 'foo'
        assert vars(b)['a*b'] == 'bar'
        assert vars(b)['c.d'] == 'fig'
        # assert vars(b) == a
