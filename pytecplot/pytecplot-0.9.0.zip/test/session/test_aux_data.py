from __future__ import unicode_literals

import os

from contextlib import contextmanager
import unittest
from unittest.mock import patch, Mock

import tecplot as tp
from tecplot.constant import PlotType
from tecplot.exception import *

from test.sample_data import loaded_sample_data
from test import patch_tecutil


class TestAuxData(unittest.TestCase):
    def setUp(self):
        with loaded_sample_data('xylines_poly') as ds:
            self.dataset = ds

    def _test_aux_data(self, aux):
        self.assertEqual(aux.as_dict(), {})
        aux['result'] = '3.1415'
        aux['other_info'] = '128'
        aux['more.info'] = 'testing\nmultiline\ninfo'

        self.assertEqual(aux['result'], '3.1415')
        self.assertEqual(aux['other_info'], '128')
        self.assertEqual(aux['more.info'], 'testing\nmultiline\ninfo')

        self.assertEqual(list(aux.keys()),
                         ['more.info', 'other_info', 'result'])
        self.assertEqual(list(aux.values()),
                         ['testing\nmultiline\ninfo', '128', '3.1415'])

        del aux['result']

        self.assertEqual(list(aux.keys()), ['more.info', 'other_info'])

        aux.update(test=5)
        aux.update({'test': 6})

        self.assertEqual(list(aux.keys()), ['more.info', 'other_info', 'test'])
        self.assertEqual(aux['test'], '6')

        with self.assertRaises(TecplotKeyError):
            x = aux['notakey']
        with patch_tecutil('AuxDataGetItemByIndex',
                           return_value=('key', 'val', 2, False)):
            with self.assertRaises(TecplotNotImplementedError):
                aux._item(0)

        self.assertEqual(aux[0], aux['more.info'])
        aux[0] = 'test'
        self.assertEqual(aux['more.info'], 'test')

        i = len(aux)
        with self.assertRaises(TecplotIndexError):
            aux[i] = 'test'

        with patch_tecutil('AuxDataSetItem', return_value=False):
            with self.assertRaises(TecplotSystemError):
                aux[0] = 'test1'

        self.assertEqual(str(aux), str(aux.as_dict()))

        l = len(aux)
        del aux[0]
        self.assertEqual(len(aux), l - 1)

        itr = iter(aux)
        item = itr.next()
        self.assertEqual(next(aux.keys()), item)

        aux.update(aa='test aa', bb='test bb')
        aux.clear()
        self.assertEqual(len(aux), 0)

    def test_layout_aux_data(self):
        self._test_aux_data(tp.layout.aux_data())

    def test_page_aux_data(self):
        self._test_aux_data(tp.active_page().aux_data)

    def test_frame_aux_data(self):
        self._test_aux_data(tp.active_frame().aux_data)

    def test_dataset_aux_data(self):
        self._test_aux_data(tp.active_frame().dataset.aux_data)

    def test_variable_aux_data(self):
        self._test_aux_data(tp.active_frame().dataset.variable(0).aux_data)

    def test_zone_aux_data(self):
        self._test_aux_data(tp.active_frame().dataset.zone(0).aux_data)

    def test_linemap_aux_data(self):
        plot = tp.active_frame().plot(PlotType.XYLine)
        self._test_aux_data(plot.linemap(0).aux_data)


if __name__ == '__main__':
    from .. import main
    main()
