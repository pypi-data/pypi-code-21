from builtins import int

import ctypes
import os
import sys
import unittest

from unittest.mock import patch, Mock

from tecplot.constant import Color, PlotType
from tecplot.exception import TecplotAttributeError, TecplotTypeError
from tecplot.tecutil import (_tecutil, Index, ListWrapper, array_to_enums,
                             array_to_str, check_arglist_argtypes, color_spec,
                             flatten_args, filled_slice, lock_attributes,
                             optional)
import tecplot

from ..sample_data import sample_data


class TestIndex(unittest.TestCase):
    def test_is_int(self):
        for i in [-2,-1,0,1,2]:
            i = Index(1)
            self.assertIsInstance(i, Index)
            self.assertIsInstance(i, int)

    def test_int_ops(self):
        x = 3
        y = Index(4)
        self.assertFalse(isinstance(x, Index))
        z = x + y
        self.assertIsInstance(z, int)
        self.assertFalse(isinstance(z, Index))


class TestFlattenArgs(unittest.TestCase):
    def test_single_str(self):
        fargs = flatten_args('test')
        self.assertEqual(fargs, tuple(['test']))

        args = 'test'
        fargs = flatten_args(args)
        self.assertEqual(fargs, tuple(['test']))

    def test_single_obj(self):
        fargs = flatten_args(1)
        self.assertEqual(fargs, tuple([1]))

        args = 1
        fargs = flatten_args(args)
        self.assertEqual(fargs, tuple([1]))
        fargs = flatten_args(tuple([args]))
        self.assertEqual(fargs, tuple([1]))
        fargs = flatten_args(list([args]))
        self.assertEqual(fargs, tuple([1]))

    def test_multiple_str(self):
        fargs = flatten_args('test1','test2')
        self.assertEqual(fargs, tuple(['test1','test2']))

        args = tuple(['test1','test2'])
        fargs = flatten_args(*args)
        self.assertEqual(fargs, tuple(['test1','test2']))
        fargs = flatten_args(args)
        self.assertEqual(fargs, tuple(['test1','test2']))
        fargs = flatten_args(list(args))
        self.assertEqual(fargs, tuple(['test1','test2']))

    def test_multiple_obj(self):
        fargs = flatten_args(1,2)
        self.assertEqual(fargs, tuple([1,2]))

        args = tuple([1,2])
        fargs = flatten_args(*args)
        self.assertEqual(fargs, tuple([1,2]))
        fargs = flatten_args(args)
        self.assertEqual(fargs, tuple([1,2]))
        fargs = flatten_args(list(args))
        self.assertEqual(fargs, tuple([1,2]))


class TestArrayToEnums(unittest.TestCase):
    def test_convert(self):
        arr = (ctypes.c_int*3)(1,2,3)
        enums = array_to_enums(arr, 3, Color)
        self.assertEqual(enums, tuple([Color.Red,Color.Green,Color.Blue]))

        parr = ctypes.cast(arr, ctypes.POINTER(ctypes.c_int))
        enums = array_to_enums(arr, 3, Color)
        self.assertEqual(enums, tuple([Color.Red,Color.Green,Color.Blue]))


class TestLockAttributes(unittest.TestCase):
    def test(self):
        @lock_attributes
        class MyClass(object):
            def __init__(self):
                self.x = 1
                self._y = 2
                self.z = 3
            @property
            def y(self):
                return self._y
            @y.setter
            def y(self,val):
                self._y = val
            @property
            def z(self):
                return self._z
            @z.setter
            def z(self,val):
                self._z = val
            @property
            def a(self):
                if not hasattr(self,'_a'):
                    self._a = 1
                return self._a
            @a.setter
            def a(self,val):
                self._a = val

        myclass = MyClass()
        myclass.a = 1
        if __debug__:
            with self.assertRaises(TecplotAttributeError):
                myclass.b = 2


class TestCheckArglistArgtypes(unittest.TestCase):
    def test_check(self):
        check_arglist_argtypes('fnname', ([float],[3.14],['vname']),
                               ([int,float],[1,None,2],['v1','v2','v3']),
                               ([str],['value'],['vname2']))
        with self.assertRaises(TecplotTypeError):
            check_arglist_argtypes('fnname', ([int],['badtype'],['vname2']))


class TestColorSpec(unittest.TestCase):
    def setUp(self):
        tecplot.new_layout()
        self.filename,dataset = sample_data('10x10x10')
        frame = tecplot.active_frame()
        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()

    def tearDown(self):
        os.remove(self.filename)

    def test_color_spec(self):
        self.assertEqual(color_spec(Color.Blue, self.plot), Color.Blue)
        self.assertEqual(color_spec(Color.MultiColor2, self.plot),
                         self.plot.contour(1))
        self.assertEqual(color_spec(Color.Blue), Color.Blue)
        self.assertEqual(color_spec(self.plot.contour(1)), Color.MultiColor2)


class TestArrayToStr(unittest.TestCase):
    def test_array_to_str(self):
        s = array_to_str(range(12))
        self.assertEqual(s, '[0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ...]')

        s = array_to_str(range(12), 3)
        self.assertEqual(s, '[0, 1, 2 ...]')

        s = array_to_str([])
        self.assertEqual(s, '[]')

        s = array_to_str([3.1415])
        self.assertEqual(s, '[3.1415]')

        s = 3.1415
        self.assertEqual(array_to_str(s), '3.1415')


class TestFilledSlice(unittest.TestCase):
    def _assert_equal(self, s, start, stop, step):
        self.assertEqual(s.start, start)
        self.assertEqual(s.stop, stop)
        self.assertEqual(s.step, step)

    def test_filled_slice(self):
        self._assert_equal(filled_slice(slice(0, 10), 10), 0, 10, 1)
        self._assert_equal(filled_slice(slice(0, 10), 9), 0, 9, 1)
        self._assert_equal(filled_slice(slice(None, 10), 9), 0, 9, 1)
        self._assert_equal(filled_slice(slice(None, None, 2), 8), 0, 8, 2)


        self._assert_equal(filled_slice(slice(-3, None), 10), 7, 10, 1)

        self._assert_equal(filled_slice(slice(-7, -3), 10), 3, 7, 1)


class TestListWrapper(unittest.TestCase):
    def test_list_wrapper(self):
        list_wrapper = ListWrapper(initial_width=15, subsequent_width=10)
        self.assertEqual(list_wrapper.fill([]), "")
        self.assertEqual(list_wrapper.fill(['a', 'b', 'c']), "'a', 'b', 'c'")
        self.assertEqual(list_wrapper.fill(
            ['a', 'b', 'c', 'd']),
            "'a', 'b', 'c',\n    'd'")
        list_wrapper.prefix = '['
        list_wrapper.suffix = ']'
        self.assertEqual(list_wrapper.fill(['a', 'b', 'cc']), "['a', 'b', 'cc'\n    ]")


class TestOptional(unittest.TestCase):
    def test_optional(self):
        class A(object):
            def __init__(self, *args):
                self.nargs = len(args)
            def __enter__(self):
                return self
            def __exit__(self, *args, **kwargs):
                pass

        with optional(A, None) as a:
            self.assertIsNone(a)
        with optional(A, 'test') as a:
            self.assertIsInstance(a, A)
            self.assertEqual(a.nargs, 1)


if __name__ == '__main__':
    from .. import main
    main()
