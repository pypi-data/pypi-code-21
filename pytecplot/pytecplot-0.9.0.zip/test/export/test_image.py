from __future__ import unicode_literals

import imghdr
import os
import unittest
import warnings
import io
from PIL import Image
from random import randint
from tempfile import NamedTemporaryFile
from unittest.mock import *

import tecplot as tp
from tecplot.exception import *
from tecplot.constant import *

from .. import patch_tecutil, closed_tempfile


class TestExport(unittest.TestCase):
    _TESTING_WIDTH = 32

    def setUp(self):
        warnings.simplefilter('ignore')

    def tearDown(self):
        warnings.simplefilter('default')

    def test_save_frame_as_jpeg(self):
        tp.new_layout()
        with closed_tempfile('.jpg') as fname:
            tp.export.save_jpeg(fname, self._TESTING_WIDTH,
                                region=tp.active_frame())
            self.assertEqual(imghdr.what(fname), 'jpeg')

    def test_failure(self):
        with patch_tecutil('Export', return_value=False):
            with self.assertRaises(TecplotSystemError):
                tp.export.save_jpeg('test.jpeg', self._TESTING_WIDTH)

    def test_save_jpeg(self):
        tp.new_layout()
        with closed_tempfile('.jpg') as fname:
            tp.export.save_jpeg(fname, self._TESTING_WIDTH)
            self.assertEqual(imghdr.what(fname), 'jpeg')

            tp.export.save_jpeg(fname, self._TESTING_WIDTH,
                                region=ExportRegion.WorkArea,
                                supersample=2, encoding=JPEGEncoding.Standard,
                                quality=10)
            self.assertEqual(imghdr.what(fname), 'jpeg')

    def test_save_png(self):
        tp.new_layout()
        with closed_tempfile('.png') as fname:
            tp.export.save_png(fname, self._TESTING_WIDTH)
            self.assertEqual(imghdr.what(fname), 'png')

            tp.export.save_png(fname, self._TESTING_WIDTH,
                               region=ExportRegion.WorkArea,
                               supersample=2, convert_to_256_colors=True)
            self.assertEqual(imghdr.what(fname), 'png')

    def test_save_tiff(self):
        tp.new_layout()
        with closed_tempfile('.tiff') as fname:
            tp.export.save_tiff(fname, self._TESTING_WIDTH)
            self.assertEqual(imghdr.what(fname), 'tiff')

    def test_save_wmf(self):
        tp.new_layout()
        with closed_tempfile('.wmf') as fname:
            tp.export.save_wmf(fname)
            with Image.open(fname) as img:
                self.assertEqual(img.format, 'WMF')

    def test_save_ps(self):
        tp.new_layout()
        with closed_tempfile('.ps') as fname:
            tp.export.save_ps(fname)
            with Image.open(fname) as img:
                self.assertEqual(img.format, 'EPS')


if __name__ == '__main__':
    from .. import main
    main()
