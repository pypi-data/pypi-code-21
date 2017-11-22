import unittest
import os

from kooki.config import get_kooki_dir

class TestKookiDir(unittest.TestCase):

    def test_env_not_set(self):
        os.environ['KOOKI_DIR'] = ''
        kooki_dir = get_kooki_dir()
        self.assertEqual(kooki_dir, os.path.expanduser('~/.kooki'))

    def test_env_set(self):
        os.environ['KOOKI_DIR'] = '/home'
        kooki_dir = get_kooki_dir()
        self.assertEqual(kooki_dir, '/home')
        os.environ['KOOKI_DIR'] = ''
