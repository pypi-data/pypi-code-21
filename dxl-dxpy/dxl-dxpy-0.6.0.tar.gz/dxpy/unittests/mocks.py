import unittest
from fs.memoryfs import MemoryFS


def make_test_fs(fs):
    fs.makedir('sub.0')
    with fs.opendir('sub.0') as sub:
        sub.makedir('subsub.0')
        with sub.opendir('subsub.0') as subsub:
            subsub.touch('test.txt')


class TestCaseWithMemoryFS(unittest.TestCase):
    def setUp(self):
        self.fs = MemoryFS()

    def tearDown(self):
        self.fs.close()
