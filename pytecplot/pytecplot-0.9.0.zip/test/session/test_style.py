from builtins import int

import ctypes
import numpy as np
import logging
import os
import platform
import sys

from ctypes import *
from contextlib import contextmanager
from enum import Enum
from textwrap import dedent
import unittest
from unittest.mock import patch, Mock

from test import patch_tecutil, skip_if_connected

import tecplot as tp
from tecplot import session
from tecplot.constant import GetValueReturnCode, SetValueReturnCode, PlotType, SurfacesToPlot, Color
from tecplot.exception import *
from tecplot.tecutil import ArgList, IndexRange, IndexSet, StringList, sv

from ..sample_data import sample_data

class TestSetStyle(unittest.TestCase):
    def setUp(self):
        self.setx_arglists = []
        def _setx(arglist,self=self):
            d = dict(arglist)
            for k,v in d.items():
                if isinstance(v,IndexSet):
                    d[k] = set(v)
            self.setx_arglists.append(d)
            return SetValueReturnCode.Ok
        self.setx = Mock(side_effect=_setx)
        self.patches = [
            patch.object(tp.tecutil._tecutil, 'StyleSetLowLevelX', self.setx),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    @skip_if_connected
    def test_log(self):
        if __debug__:
            loglevel = logging.root.getEffectiveLevel()
            logging.root.setLevel(logging.DEBUG)
            with patch.object(tp.session.style.log, 'debug', Mock()) as log:
                tp.session.set_style('value',sv.P1,sv.P2,key1='key1value')
                self.assertEqual(log.call_args_list[0][0][0], dedent('''\
                    SetStyle
                      value: value
                      {0} P1
                      {0} P2
                      key1 : {0} key1value'''.format(type(str()))))
                self.assertEqual(log.call_args_list[1][0][0], dedent('''\
                    SetStyle
                      P1: P1
                      P2: P2
                      STRVALUE: value
                      KEY1: key1value'''))
            logging.root.setLevel(loglevel)

    def test_enum(self):
        class MyEnum(Enum):
            Key = 2
        tp.session.set_style(MyEnum.Key)
        self.assertEqual(self.setx_arglists[-1], {sv.IVALUE:MyEnum.Key.value})

    def test_index(self):
        i = tp.tecutil.Index(4)
        tp.session.set_style(i)
        arglist = self.setx_arglists[-1]
        self.assertEqual(arglist, {sv.IVALUE:i+1})

    def test_int(self):
        i = 4
        tp.session.set_style(i)
        arglist = self.setx_arglists[-1]
        self.assertEqual(arglist, {sv.IVALUE:4})

        if __debug__:
            with self.assertRaises((TecplotOverflowError, TecplotTypeError)):
                tp.session.set_style(2**64 + 1)

    def test_bool(self):
        i = True
        tp.session.set_style(i)
        arglist = self.setx_arglists[-1]
        self.assertEqual(arglist, {sv.IVALUE:1})

    def test_float(self):
        i = 3.1415
        tp.session.set_style(i)
        arglist = self.setx_arglists[-1]
        self.assertEqual(list(arglist.keys()),[sv.DVALUE])
        self.assertTrue(np.isclose(arglist[sv.DVALUE], 3.1415))

    def test_str(self):
        i = 'test'
        tp.session.set_style(i)
        arglist = self.setx_arglists[-1]
        self.assertEqual(arglist, {sv.STRVALUE:'test'})

    def test_lists(self):

        def _setx(arglist,self=self):
            addr = ctypes.c_size_t(arglist[sv.IVALUE])
            ptr = ctypes.c_void_p(addr.value)
            iset = ctypes.cast(ptr, IndexSet)
            self.assertEqual(set(iset), {1,2,3})
            return SetValueReturnCode.Ok
        setx = Mock(side_effect=_setx)
        with patch.object(tp.tecutil._tecutil, 'StyleSetLowLevelX', setx):
            tp.session.set_style({1,2,3})

    def test_index_range(self):
        i = IndexRange(3,30,2)
        tp.session.set_style(i)
        imin,imax,istep = self.setx_arglists[-3:]
        self.assertEqual(imin, {sv.P1:sv.MIN,sv.IVALUE:i.min+1})
        self.assertEqual(imax, {sv.P1:sv.MAX,sv.IVALUE:i.max+1})
        self.assertEqual(istep, {sv.P1:sv.SKIP,sv.IVALUE:i.step})

    def test_stringlist(self):
        def _setx(arglist,self=self):
            addr = ctypes.c_size_t(arglist[sv.IVALUE])
            ptr = ctypes.c_void_p(addr.value)
            iset = ctypes.cast(ptr, StringList)
            self.assertEqual(list(iset), ['aa','bb'])
            return SetValueReturnCode.Ok
        setx = Mock(side_effect=_setx)
        with patch.object(tp.tecutil._tecutil, 'StyleSetLowLevelX', setx):
            tp.session.set_style(['aa','bb'])

    def test_errors(self):
        class UnknownType(object):
            pass
        with self.assertRaises(TecplotTypeError):
            tp.session.set_style(UnknownType())

        def _setx(arglist,self=self):
            return SetValueReturnCode.ValueSyntaxError
        setx = Mock(side_effect=_setx)
        with patch.object(tp.tecutil._tecutil, 'StyleSetLowLevelX', setx):
            with self.assertRaises(TecplotSystemError):
                tp.session.set_style(1)

        with patch_tecutil('StyleSetLowLevelX', side_effect=TecplotLogicError):
            with self.assertRaises(TecplotLogicError):
                tp.session.set_style(1)

    def test_kwargs(self):
        uid = 2
        objset = {3,4}
        off1 = 5
        off2 = 6
        tp.session.set_style(0, **{sv.UNIQUEID:uid, sv.OBJECTSET:objset,
            sv.OFFSET1: off1, sv.OFFSET2: off2})
        al = self.setx_arglists[-1]
        self.assertEqual(al[sv.UNIQUEID], 2)
        self.assertEqual(al[sv.OBJECTSET], {3,4})
        self.assertEqual(al[sv.OFFSET1], 5+1)
        self.assertEqual(al[sv.OFFSET2], 6+1)

class TestGetStyle(unittest.TestCase):
    def setUp(self):
        if tp.tecutil._tecutil_connector.connected:
            raise unittest.SkipTest('batch only tests')

    def test_int(self):
        def modify_arglist(al):
            # print(type(al[sv.IVALUE]), al[sv.IVALUE])
            al[sv.IVALUE][0] = 1
            return GetValueReturnCode.Ok
        with patch_tecutil('StyleGetLowLevelX', side_effect=modify_arglist):
            self.assertEqual(tp.session.get_style(int), 1)

    def test_log(self):
        if __debug__:
            loglevel = logging.root.getEffectiveLevel()
            logging.root.setLevel(logging.DEBUG)
            class UnknownType(object):
                pass
            with patch_tecutil('StyleGetLowLevelX',
                               return_value=GetValueReturnCode.Ok):
                with patch.object(tp.session.style.log, 'debug', Mock()) as log:
                    tp.session.get_style(UnknownType,sv.P1,sv.P2,key1='key1value')
                    self.assertEqual(log.call_args_list[0][0][0], dedent('''\
                        GetStyle
                          {0} P1
                          {0} P2
                          key1 : {0} key1value'''.format(type(str()))))
                    self.assertEqual(log.call_args_list[1][0][0], dedent('''\
                        GetStyle
                          P1: P1
                          P2: P2
                          KEY1: key1value'''))
            logging.root.setLevel(loglevel)

    def test_index_range(self):
        def fn(al):
            al[sv.IVALUE][0] = 4
            return GetValueReturnCode.Ok
        with patch_tecutil('StyleGetLowLevelX', side_effect=fn):
            self.assertEqual(tp.session.get_style(IndexRange), IndexRange(3,3,4))

    def test_kwargs(self):
        def fn(al):
            self.assertEqual(al[sv.UNIQUEID], 2)
            self.assertEqual(al[sv.OBJECTSET], {3,4})
            self.assertEqual(al[sv.OFFSET1], 5+1)
            self.assertEqual(al[sv.OFFSET2], 6+1)
            return GetValueReturnCode.Ok
        class UnknownType(object):
            pass
        uid = 2
        objset = {3,4}
        off1 = 5
        off2 = 6
        with patch_tecutil('StyleGetLowLevelX', side_effect=fn):
            tp.session.get_style(UnknownType, **{sv.UNIQUEID:uid,
                sv.OBJECTSET:objset, sv.OFFSET1: off1, sv.OFFSET2: off2})

    def test_float(self):
        v = 3.14
        def modify_arglist(al,v=v):
            al[sv.DVALUE][0] = v
            return GetValueReturnCode.Ok
        with patch_tecutil('StyleGetLowLevelX', side_effect=modify_arglist):
            self.assertEqual(tp.session.get_style(float), v)

    def test_errors(self):
        def fn(al):
            return GetValueReturnCode.SyntaxError
        with patch_tecutil('StyleGetLowLevelX', side_effect=fn):
            with self.assertRaises(TecplotSystemError):
                tp.session.get_style(str)

        with patch_tecutil('StyleGetLowLevelX', side_effect=TecplotLogicError):
            with self.assertRaises(TecplotLogicError):
                tp.session.get_style(int)

    def test_enum(self):
        class MyEnum(Enum):
            A = 0
            B = 1
        v = MyEnum.B
        def modify_arglist(al,v=v):
            al[sv.IVALUE][0] = v.value
            return GetValueReturnCode.Ok
        with patch_tecutil('StyleGetLowLevelX', side_effect=modify_arglist):
            self.assertEqual(tp.session.get_style(MyEnum), v)

    def test_list(self):
        v = [1,2,3]
        def modify_arglist(al,v=v):
            iset = IndexSet(*v)
            al[sv.IVALUE][0] = addressof(cast(iset,POINTER(c_int64)).contents)
            return GetValueReturnCode.Ok
        with patch_tecutil('StyleGetLowLevelX', side_effect=modify_arglist):
            self.assertEqual(tp.session.get_style(list), v)

    def test_bool(self):
        v = False
        def fn(al,v=v):
            al[sv.IVALUE][0] = v
            return GetValueReturnCode.Ok
        with patch_tecutil('StyleGetLowLevelX', side_effect=fn):
            self.assertEqual(tp.session.get_style(bool), v)

        v = True
        def fn(al,v=v):
            al[sv.IVALUE][0] = v
            return GetValueReturnCode.Ok
        with patch_tecutil('StyleGetLowLevelX', side_effect=fn):
            self.assertEqual(tp.session.get_style(bool), v)

    def test_str(self):
        s = c_char_p(b'abc')
        def modify_arglist(al,s=s):
            addr = addressof(cast(s, POINTER(c_char)).contents)
            ptr = pointer(c_int64(addr))
            al[sv.IVALUE][0] = ptr.contents
            return GetValueReturnCode.Ok
        with patch_tecutil('StyleGetLowLevelX', side_effect=modify_arglist):
            self.assertEqual(tp.session.get_style(str), s.value.decode())

class TestStyle(unittest.TestCase):
    def setUp(self):
        self.filename,self.dataset = sample_data('10x10x10')
        frame = tp.active_frame()

        frame.plot_type = PlotType.Cartesian3D
        self.plot = frame.plot()
        contour = self.plot.contour(0)
        contour.variable_index = self.dataset.variable('Z').index
        fieldmap = self.plot.fieldmap(0)
        fieldmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        self.plot.show_contour = True

        self.override = frame.plot().contour(0).colormap_filter.override(0)
        self.override_style = session.Style(*self.override._sv,
            offset1=contour.index, offset2=self.override.index)

        self.plot_style = session.Style(*self.plot._sv)

    def tearDown(self):
        os.remove(self.filename)

    def test_nouid_offset1_offset2(self):
        for val in [Color.Red,Color.Blue]:
            self.override_style._set_style(val,sv.COLOR)
            self.assertEqual(self.override_style._get_style(Color,sv.COLOR),
                             self.override.color)
            self.assertEqual(self.override.color, val)

    def test_nouid_nooffset(self):
        for val in [True,False,True]:
            self.plot_style._set_style(val, sv.SHOWCONTOUR)
            self.assertEqual(self.plot_style._get_style(bool, sv.SHOWCONTOUR),
                             self.plot.show_contour)
            self.assertEqual(self.plot.show_contour, val)

    def test_offset1(self):
        y,z = (self.dataset.variable(x) for x in ['Y','Z'])
        ctr = self.plot.fieldmap(0).contour
        ctr.flood_contour_group = self.plot.contour(0)
        ctr.line_group = self.plot.contour(1)
        ctr.flood_contour_group.variable = y
        ctr.line_group.variable = z
        self.assertEqual(ctr.flood_contour_group.variable, y)
        self.assertEqual(ctr.line_group.variable, z)
        ctr.flood_contour_group.variable = z
        ctr.line_group.variable = y
        self.assertEqual(ctr.flood_contour_group.variable, z)
        self.assertEqual(ctr.line_group.variable, y)

    def test_cached_style_attrs(self):
        style = session.Style('A','B',uniqueid=1,offset=1,multiset=False)
        cache = style._style_attrs
        self.assertEqual(cache, style._cached_style_attrs)
        self.assertEqual(cache, style._style_attrs)


if __name__ == '__main__':
    from .. import main
    main()
