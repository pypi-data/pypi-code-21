import pytest
import unittest
import unittest.mock as mock
import tempfile
import shutil
import pathlib
from dxpy.file_system.file_system import FileSystem as fs
from dxpy.file_system.path import Path


class TestFileSystem(unittest.TestCase):
    def setUp(self):
        dpath = tempfile.mkdtemp()
        pdr = pathlib.Path(dpath)
        pd1 = pdr / 'sub1'
        pd1.mkdir()
        pd2 = pdr / 'sub2'
        pd2.mkdir()
        pf1 = pdr / 'tmp.txt'
        pf1.touch()
        pf2 = pdr / 'tmp2.txt'
        pf2.touch()
        pf3 = pdr / 'tmp4.txt'
        pf3.touch()
        with open(pf3, 'w') as fout:
            print('test3', file=fout)
        pd6 = pdr / 'sub6'
        pd6.mkdir()
        pd7 = pd6 / 'sub7'
        pd7.mkdir()
        pf4 = pd6 / 'test.txt'
        pf4.touch()
        self.root = dpath

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_exists(self):
        def pos():
            file1 = str((pathlib.Path(self.root) / 'tmp.txt').absolute())
            assert fs.exists(Path(file1))

        def neg():
            file1 = str((pathlib.Path(self.root) / 'tmpx.txt').absolute())
            assert not fs.exists(Path(file1))
        pos()
        neg()

    def test_is_file(self):
        assert fs.File.check(Path(self.root + '/tmp.txt'))
        assert not fs.File.check(Path(self.root + '/tmpx.txt'))
        assert not fs.File.check(Path(self.root + '/sub1'))

    def test_create_file(self):
        path = Path(self.root + '/tmp3.txt')
        fs.File.create(path)
        assert fs.exists(path)

    def test_delete_file(self):
        path = Path(self.root + '/tmp2.txt')
        fs.File.delete(path)
        assert not fs.exists(path)

    def test_create_directory(self):
        path = Path(self.root + '/sub3')
        fs.Directory.create(path)
        assert fs.exists(path)

    def test_is_dir(self):
        assert fs.Directory.check(Path(self.root + '/sub1'))
        assert not fs.Directory.check(Path(self.root + '/subx'))
        assert not fs.Directory.check(Path(self.root + '/tmp.txt'))

    def test_delete_directory(self):
        path = Path(self.root + '/sub2')
        fs.Directory.delete(path)
        assert not fs.exists(path)

    def test_glob(self):
        result = fs.Directory.glob(Path(self.root + '/sub6'))
        assert set(result) == {self.root + '/sub6/sub7',
                               self.root + '/sub6/test.txt'}

    def test_copy(self):
        # TODO
        pass

    def test_move(self):
        # TODO
        pass
