from __future__ import unicode_literals, with_statement

import ctypes
import numpy as np
import os
import platform
import re
import sys

from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from textwrap import dedent

import unittest
from unittest.mock import patch, Mock, PropertyMock

import tecplot as tp
from tecplot import layout
from tecplot.exception import *
from tecplot.constant import *
from tecplot.data import operate as op
from tecplot.tecutil import _tecutil, ArgList

class TestCreateOrderedZone(unittest.TestCase):
    #def test_1d(self):
    #    page = tp.active_page()
    #    frame = page.add_frame()
    #    z1 = tp.data.create_ordered_zone('zone1', 'x', 100, (-10,10))
    #    z2 = tp.data.create_ordered_zone('zone2', ('x',), 100, (-10,10))
    #    z3 = tp.data.create_ordered_zone('zone3', 'x', (100,), (-10,10))
    #    z4 = tp.data.create_ordered_zone('zone4', 'x', 100, ((-10,10),))
    #    z5 = tp.data.create_ordered_zone('zone5', ('x',), (100,), ((-10,10),))
    #    z6 = tp.data.create_ordered_zone('zone6', ['x'], [100], [(-10,10)])
    #
    #z = tp.data.create_ordered_zone('z3d', position_variables['x','y','z'],
    #    data_variables = ['pressure', 'color'], shape=(10,10,10),
    #    limits=[(0,10),(0,1),(-10,10)],
    #    position_dtypes=FieldDataType.Float,
    #    data_dtypes=[FieldDataType.Double, FieldDataType.Int])

    def create_ordered_zone(self):
        page = tp.active_page()
        frame = page.add_frame()

        self.assertFalse(_tecutil.DataSetIsAvailableForFrame(frame.uid))

        dataset = frame.create_dataset('dataset title')

        print('dataset uid:',dataset.uid)
        self.assertIsNotNone(frame.dataset)
        self.assertEqual(dataset, frame.dataset)

        vv = 'a b c'.split()
        variables = []
        for v in vv:
            variables.append(dataset.add_variable(v))

        zone = dataset.add_zone(ZoneType.Ordered, 'Zone name', 11)

        x = np.linspace(0,10,11)
        y = np.sin(x)

        a = zone.values('a')
        b = zone.values('b')

        a[:] = x
        b[:] = y

        print(frame.dataset)
        print('\n'.join(str(x) for x in variables))
        print(zone)
        print(zone.shape)
        print(zone.variables('a')[:])
        print(zone.variables('b')[:])

        with ArgList() as a:
            a['aa'] = [ValueLocation.CellCentered,
                       ValueLocation.CellCentered,
                       ValueLocation.Nodal,
                       ValueLocation.CellCentered]
            aa = tp.tecutil.array_to_enums(a['aa'], 4, ValueLocation)
            print(aa)


if __name__ == '__main__':
    from .. import main
    main()
