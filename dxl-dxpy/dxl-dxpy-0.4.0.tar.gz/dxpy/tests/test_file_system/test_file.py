import pytest
import unittest
from unittest.mock import MagicMock, patch
import pathlib
import json
from dxpy.file_system.path import Path
import dxpy.file_system.file as fi
from dxpy.file_system.file_system import FileSystem
import tempfile
import shutil


def _is_dir_made_true(path):
    return True


def _is_dir_made_false(path):
    return False


def _is_file_made_true(path):
    return True


def _is_file_made_false(path):
    return False


def _exists_made_true(obj):
    return True


class TestFileAbstract(unittest.TestCase):
    @patch.multiple(fi.FileAbstract, __abstractmethods__=set())
    def test_check(self):
        def pos():
            fs = MagicMock()
            fs.exists.return_value = True
            assert fi.FileAbstract.check('/tmp/test', fs)

        def neg():
            fs = MagicMock()
            fs.exists.return_value = False
            assert not fi.FileAbstract.check('/tmp/test', fs)

        pos()
        neg()

    @patch.multiple(fi.FileAbstract, __abstractmethods__=set())
    def test_check_fail(self):
        try:
            fs = MagicMock()
            fs.exists.return_value = False
            fi.FileAbstract('/tmp/test', fs)
            self.fail("FileNotFoundOrWrongTypeError not thrown.")
        except fi.FileNotFoundOrWrongTypeError as e:
            assert True

    def test_copy_to(self):
        # TODO
        pass

    def test_move_to(self):
        # TODO
        pass

    @patch.multiple(fi.FileAbstract, __abstractmethods__=set())
    def test_ftype(self):
        fs = MagicMock()
        fs.exists.return_value = True
        assert fi.FileAbstract('/tmp', fs).ftype == {'FileAbstract'}

    @patch.multiple(fi.FileAbstract, __abstractmethods__=set())
    def test_brief(self):
        fs = MagicMock()
        fs.exists.return_value = True
        assert fi.FileAbstract('/tmp/test', fs).brief == {
            'path': '/tmp/test',
            'name': 'test',
            'type': ['FileAbstract']
        }

    @patch.multiple(fi.FileAbstract, __abstractmethods__=set())
    def test_detail(self):
        fs = MagicMock()
        fs.exists.return_value = True
        assert fi.FileAbstract('/tmp/test', fs).detail == {
            'path': '/tmp/test',
            'name': 'test',
            'type': ['FileAbstract'],
            'parent': '/tmp',
            'parts': ('/', 'tmp', 'test')
        }


class TestDirectory(unittest.TestCase):
    def setUp(self):
        dpath = tempfile.mkdtemp()
        pdr = pathlib.Path(dpath)
        pd1 = pdr / 'sub1'
        pd1.mkdir()
        pd2 = pdr / 'sub2'
        pd2.mkdir()
        pf1 = pdr / 'tmp.txt'
        pf1.touch()
        self.root = dpath

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_check_pos(self):
        assert fi.Directory.check(self.root + '/sub1', FileSystem)

    def test_check_pos_deffac(self):
        assert fi.Directory.check(self.root + '/sub1', FileSystem)

    def test_check_neg(self):
        assert not fi.Directory.check(self.root + '/tmp.txt', FileSystem)

    def test_init_check_fail(self):
        try:
            fi.Directory(self.root + '/sub3', FileSystem, fi.FileFactory)
            self.fail("FileNotFoundOrWrongTypeError not thrown.")
        except fi.FileNotFoundOrWrongTypeError as e:
            assert True

    def test_ftype(self):
        assert fi.Directory(self.root + '/sub1', FileSystem,
                            fi.FileFactory).ftype == {'FileAbstract', 'Directory'}

    def test_brief(self):
        types = ['FileAbstract', 'Directory']
        types.sort()
        assert fi.Directory(self.root + '/sub1', FileSystem, fi.FileFactory).brief == {
            'path': self.root + '/sub1',
            'name': 'sub1',
            'type': types
        }

    def test_detail(self):
        # print(fi.Directory(self.root, FileSystem).detail)
        # assert 0
        pass

    