import unittest
from fs.memoryfs import MemoryFS


class TestFileFilter(unittest.TestCase):
    def setUp(self):
        self.fs = MemoryFS()
        for i in range(5):
            self.fs.makedir('sub.{0}'.format(i))

    def tearDown(self):
        self.fs.close()
