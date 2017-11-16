from __future__ import unicode_literals, with_statement

import os
import re
import sys

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

from ..sample_data import loaded_sample_data

_TECUTIL_VALID_ID = TECUTIL_BAD_ID + 1

if sys.version_info >= (3,):
    long = int

class TestPages(unittest.TestCase):

    def test_active_page(self):
        page = tp.active_page()
        self.assertTrue(page.active)

    def test_activate_page(self):
        page1 = tp.add_page()
        page2 = tp.add_page()
        self.assertFalse(page1.active)
        self.assertTrue(page2.active)
        page1.activate()
        self.assertTrue(page1.active)
        self.assertFalse(page2.active)

        tp.delete_page(page1)
        self.assertRaises(TecplotRuntimeError, page1.activate)

    def test_add_page(self):
        page = tp.add_page()
        self.assertIsInstance(page.uid, (int, long))
        self.assertGreater(page.uid, 0)
        with patch_tecutil('PageCreateNew', return_value=False):
            self.assertRaises(TecplotSystemError, tp.add_page)

    def test_next_page(self):
        page1 = tp.add_page()
        page2 = tp.add_page()
        self.assertNotEqual(page1, page2)
        next_page = tp.layout.next_page()
        self.assertNotEqual(next_page, page1)

    @staticmethod
    @contextmanager
    def pages(names=['aa', 'ab', 'bb']):
        tp.new_layout()
        initial_page = tp.active_page()
        pages = []
        uids = []
        for n in names:
            pages.append(tp.add_page())
            uids.append(pages[-1].uid)
            pages[-1].name = n
        tp.delete_page(initial_page)
        yield pages

    def test_pages(self):
        names = ['aa', 'ab', 'bb']
        with TestPages.pages(names):
            self.assertEqual(len(list(tp.pages())), 3)
            self.assertEqual(len(list(tp.pages('aa'))), 1)
            self.assertEqual(len(list(tp.pages('a*'))), 2)
            self.assertEqual(len(list(tp.pages('x'))), 0)

    def test_page(self):
        names = ['aa', 'ab', 'bb']
        with TestPages.pages(names) as pages:
            self.assertEqual(tp.page('aa'), pages[0])
            self.assertEqual(tp.page('ab'), pages[1])
            self.assertEqual(tp.page('x'), None)

class TestPage(unittest.TestCase):
    @staticmethod
    @contextmanager
    def active_page():
        page = tp.add_page()
        yield page

    @staticmethod
    @contextmanager
    def non_active_page():
        tp.new_layout()
        page = tp.active_page()
        active_page = tp.add_page()
        yield page, active_page

    @staticmethod
    @contextmanager
    def deleted_page():
        page = tp.add_page()
        tp.delete_page(page)
        yield page

    # noinspection PyDefaultArgument
    @staticmethod
    @contextmanager
    def frames(names=['aa', 'ab', 'bb']):
        with TestPage.active_page() as page:
            initial_frame = page.active_frame()
            for n in names:
                f = page.add_frame()
                f.name = n
            page.delete_frame(initial_frame)
            yield page

    def test_name(self):
        with TestPage.active_page() as page:
            page.name = 'Test'
            self.assertEqual(page.name, 'Test')

        with TestPage.deleted_page() as page:
            with self.assertRaises(TecplotRuntimeError):
                self.assertFalse(page.active)
                self.assertFalse(page.exists)
                page.name = 'Test'
            with self.assertRaises(TecplotRuntimeError):
                # noinspection PyStatementEffect
                page.name

    def test_add_frame(self):
        with TestPage.active_page() as page:
            frame = page.add_frame()
            self.assertIsInstance(frame, tp.layout.Frame)
            self.assertIsInstance(frame.uid, (int, long))
            self.assertGreater(frame.uid, 0)
            self.assertEqual(frame.page.uid, page.uid)

        with TestPage.deleted_page() as page:
            self.assertRaises(TecplotRuntimeError, page.add_frame)

    def test_delete(self):
        page = tp.add_page()
        tp.delete_page(page)
        next_page = tp.active_page()
        self.assertNotEqual(page, next_page)
        self.assertRaises(TecplotRuntimeError, page.activate)
        self.assertTrue(next_page.active)
        self.assertFalse(page.active)

    def test_exists(self):
        page = tp.add_page()
        self.assertTrue(page.exists)
        tp.delete_page(page)
        self.assertFalse(page.exists)

    def test___eq__(self):
        p1 = tp.layout.Page(1)
        p2 = tp.layout.Page(2)
        self.assertNotEqual(p1, p2)
        self.assertEqual(p1, tp.layout.Page(1))

    def test_frame(self):
        with TestPage.frames(['aa', 'ab', 'bb']) as page:
            frame = page.frame('bb')
            self.assertEqual(page['bb'], frame)
            self.assertTrue(isinstance(frame, tp.layout.Frame))
            self.assertIsInstance(frame.uid, (int, long))
            self.assertGreater(frame.uid, 0)
            with patch_tecutil('FrameGetCount', return_value=0):
                with self.assertRaises(TecplotPatternMatchError):
                    frame = page.frame('bb')
            with self.assertRaises(TecplotPatternMatchError):
                frame = page.frame('not a frame name')

    def test_frames(self):
        names = ['aa', 'ab', 'bb']
        with TestPage.frames(names) as page:
            frames = page.frames()
            self.assertEqual(len(frames), 3)
            frame_names = [f.name for f in frames]
            for n in names:
                self.assertIn(n, frame_names)
            for n,f in zip(names, sorted(f.name for f in page)):
                self.assertEqual(n,f)
            with patch_tecutil('FrameGetCount', return_value=0):
                self.assertEqual(len(list(page.frames())), 0)
            with patch_tecutil('FrameGetName', return_value=(False,None)):
                self.assertEqual(len(list(page.frames())), 0)
            with self.assertRaises(TecplotPatternMatchError):
                f = page.frames('no match')

    def test___str__(self):
        with TestPage.active_page() as page:
            page.name = 'Test'
            self.assertEqual(str(page), 'Page: "Test"')

    def test___repr__(self):
        ptrn = re.compile('Page\(uid=\d+\)')
        with TestPage.active_page() as page:
            self.assertRegex(repr(page), ptrn)

    def test_in(self):
        with TestPage.active_page() as page1:
            with TestPage.active_page() as page2:
                f1a = page1.add_frame()
                f2a = page2.add_frame()
                f2b = page2.add_frame()
                self.assertIn(f1a, page1)
                self.assertIn(f2a, page2)
                self.assertIn(f2b, page2)
                self.assertNotIn(f1a, page2)
                self.assertNotIn(f2a, page1)
                self.assertNotIn(f2b, page1)
                with patch_tecutil('FrameGetCount', return_value=0):
                    self.assertNotIn(f1a, page1)

    def test_active_frame(self):
        with TestPage.frames() as page:
            frame = page.active_frame()
            self.assertIn(frame, page)
            self.assertTrue(frame.active)
            with patch_tecutil('FrameGetCount', return_value=0):
                self.assertIsNone(page.active_frame())

    def test_position(self):
        tp.new_layout()
        p0 = tp.active_page()
        p1 = tp.add_page()
        self.assertEqual(p0.position, 1)
        self.assertEqual(p1.position, 0)
        p0.activate()
        self.assertEqual(p0.position, 0)
        self.assertEqual(p1.position, 1)

    def test_name(self):
        p = tp.active_page()
        with patch_tecutil('PageSetName', return_value=False):
            with self.assertRaises(TecplotSystemError):
                p.name = 'name'

    def test_activate(self):
        p = tp.active_page()
        tp.add_page()
        with patch_tecutil('PageSetCurrentByUniqueID', return_value=False):
            with self.assertRaises(TecplotSystemError):
                p.activate()

    def test_add_frame(self):
        p = tp.active_page()
        with patch_tecutil('FrameCreateNew', return_value=False):
            with self.assertRaises(TecplotSystemError):
                p.add_frame()
        with patch_tecutil('FrameGetActiveID', return_value=-1):
            with self.assertRaises(TecplotRuntimeError):
                p.add_frame()

    def test_delete_frame(self):
        p = tp.active_page()
        f = p.active_frame()
        with patch_tecutil('FrameDeleteActive', return_value=False):
            with self.assertRaises(TecplotSystemError):
                p.delete_frame(f)
        p.delete_frame(f)
        with self.assertRaises(TecplotRuntimeError):
            p.delete_frame(f)

    def test_tile_frames(self):
        tp.new_layout()
        page = tp.active_page()
        page.add_frame()
        page.add_frame()
        page.add_frame()
        page.tile_frames(tp.constant.TileMode.Wrap)


class TestPaper(unittest.TestCase):
    def test_dimensions(self):
        with TestPage.active_page() as page:
            page.activate()
            w, h = page.paper.dimensions
            self.assertEqual(w, 11.)
            self.assertEqual(h, 8.5)


if __name__ == '__main__':
    from .. import main
    main()
