from __future__ import unicode_literals, with_statement

import os
import re

from contextlib import contextmanager
from tempfile import NamedTemporaryFile

import unittest
from .. import patch_tecutil
from unittest.mock import patch

import tecplot as tp
import tecplot.plot
from tecplot.exception import *
from tecplot.constant import *
from tecplot.constant import TECUTIL_BAD_ID
from tecplot.tecutil import sv

from test import patch_tecutil
from ..sample_data import loaded_sample_data

_TECUTIL_VALID_ID = TECUTIL_BAD_ID + 1

class TestLayouts(unittest.TestCase):
    def test_new_layout(self):
        self.assertIsNone(tp.new_layout())

    def test_load_layout(self):
        f = NamedTemporaryFile(delete=False)
        try:
            f.write(b'#!MC 1410\n')
            f.close()
            self.assertIsNone(tp.load_layout(f.name))
            with patch_tecutil('OpenLayoutX', return_value=False):
                with self.assertRaises(TecplotSystemError):
                    tp.load_layout(f.name)
        finally:
            os.remove(f.name)
        self.assertRaises(OSError, tp.load_layout,
                          '/nonexistent/path/to/layout/file.lay')

    def test_save_layout_default_arguments(self):
        def fake_save_layout(arglist):
            for option in [sv.INCLUDEDATA, sv.INCLUDEPREVIEW,
                           sv.USERELATIVEPATHS, sv.POSTLAYOUTCOMMANDS,
                           sv.PAGELIST]:

                with self.assertRaises(TypeError):
                    # Accessing the arglist option should raise a TypeError
                    # since that option should not exist in the incoming
                    # arglist.

                    # noinspection PyStatementEffect
                    arglist[option]

            return True

        with patch_tecutil('SaveLayoutX', side_effect=fake_save_layout):
            tp.save_layout(filename='filename')

    def test_save_layout_arguments(self):
        filename = 'filename'
        include_data = True
        include_preview = True
        use_relative_paths = True
        post_layout_commands = 'post_layout_commands'
        page_list = [tp.active_page()]

        def fake_save_layout(arglist):
            self.assertEqual(arglist[sv.FNAME], filename)
            self.assertTrue(arglist[sv.INCLUDEDATA])
            self.assertTrue(arglist[sv.INCLUDEPREVIEW])
            self.assertTrue(arglist[sv.USERELATIVEPATHS])
            self.assertEqual(arglist[sv.POSTLAYOUTCOMMANDS], post_layout_commands)

            pages = [P for P in arglist[sv.PAGELIST]]
            self.assertListEqual([0], pages)
            return True

        with patch_tecutil('SaveLayoutX', side_effect=fake_save_layout):
            tp.save_layout(filename=filename, include_data=include_data,
                           include_preview=include_preview,
                           use_relative_paths=use_relative_paths,
                           post_layout_commands=post_layout_commands,
                           pages=page_list)

    def test_save_layout_parameter_types(self):
        if __debug__:
            with self.assertRaises(TecplotTypeError):
                tp.save_layout(filename=1)
            with self.assertRaises(TecplotTypeError):
                tp.save_layout(filename='a', include_data=3)
            with self.assertRaises(TecplotTypeError):
                tp.save_layout(filename='a', include_preview=3)
            with self.assertRaises(TecplotTypeError):
                tp.save_layout(filename='a', use_relative_paths=3)
            with self.assertRaises(TecplotTypeError):
                tp.save_layout(filename='a', post_layout_commands=3)
            with self.assertRaises(TecplotTypeError):
                tp.save_layout(filename='a', pages=3)

    def test_save_layout(self):
        tp.new_layout()
        with NamedTemporaryFile(suffix='.lay', delete=False) as f:
            f.close()
            self.assertIsNone(tp.save_layout(f.name))
            os.remove(f.name)

    def test_save_layout_return_value(self):
        def fake_save_layout(arglist):
            return False

        with patch_tecutil('SaveLayoutX', side_effect=fake_save_layout):
            with self.assertRaises(TecplotSystemError):
                tp.save_layout(filename='filename')

    def test_add_page(self):
        p0 = tp.active_page()
        p1 = tp.add_page()
        self.assertNotEqual(p0, tp.active_page())
        self.assertEqual(p1, tp.active_page())
        with patch_tecutil('PageCreateNew', return_value=False):
            with self.assertRaises(TecplotSystemError):
                tp.add_page()

    def test_delete_page(self):
        p = tp.add_page()
        self.assertEqual(p, tp.active_page())
        tp.delete_page(p)
        self.assertNotEqual(p, tp.active_page())

    def test_next_page(self):
        p0 = tp.add_page()
        p1 = tp.add_page()
        p0.activate()
        self.assertEqual(p0, tp.active_page())
        tp.next_page()
        self.assertEqual(p1, tp.active_page())

    def test_page(self):
        tp.new_layout()
        p0 = tp.add_page()
        p0.name = 'AA'
        p1 = tp.add_page()
        p1.name = 'AB'
        p2 = tp.add_page()
        p2.name = 'BB'
        self.assertEqual(p0, tp.page('AA'))
        self.assertEqual(p0, tp.page('A*'))
        self.assertEqual(p2, tp.page('B*'))
        self.assertIsNone(tp.page('C'))

    def test_active_frame(self):
        f0 = tp.active_page().add_frame()
        f1 = tp.active_page().add_frame()
        self.assertNotEqual(f0, tp.active_frame())
        self.assertEqual(f1, tp.active_frame())

    def test_frames(self):
        tp.new_layout()
        p0 = tp.active_page()
        p0.name = 'AA'
        p1 = tp.add_page()
        p1.name = 'AB'
        p2 = tp.add_page()
        p2.name = 'BB'
        p0.active_frame().name = 'FAA'
        p1.active_frame().name = 'FAB'
        p2.active_frame().name = 'FBB'

        p0.add_frame().name = 'GAA'
        p1.add_frame().name = 'GAB'
        p2.add_frame().name = 'GBB'

        self.assertEqual(sorted([f.name for f in tp.frames('F*')]),
                         ['FAA','FAB','FBB'])
        self.assertEqual(sorted([f.name for f in tp.frames('G*')]),
                         ['GAA','GAB','GBB'])
        self.assertEqual(sorted([f.name for f in tp.frames('F*', 'AA')]),
                         ['FAA'])


if __name__ == '__main__':
    from .. import main
    main()
