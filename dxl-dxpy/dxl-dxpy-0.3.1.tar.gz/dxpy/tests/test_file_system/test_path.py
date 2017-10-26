import unittest
from unittest.mock import MagicMock
from dxpy.file_system.path import Path


class TestPath(unittest.TestCase):
    def test_str_root(self):
        p = Path('/')
        self.assertEqual(p.abs, '/')

    def test_str_basic(self):
        p = Path('/tmp')
        self.assertEqual(p.abs, '/tmp')

    def test_url(self):
        p = Path('%252Ftmp')
        self.assertEqual(p.abs, '/tmp')

    def test_parts(self):
        p = Path('/tmp/base')
        self.assertEqual(p.parts(), ('/', 'tmp', 'base'))

    def test_parent(self):
        p = Path('/tmp/base')
        self.assertEqual(p.parent, '/tmp')

    def test_name(self):
        p = Path('/tmp/base')
        self.assertEqual(p.name, 'base')

    def test_name_dir(self):
        p = Path('/tmp/base/')
        self.assertEqual(p.name, 'base')

    def test_brief(self):
        p = Path('/tmp/test')
        self.assertEqual(p.brief, {
            'name': 'test',
            'path': '/tmp/test'
        })

    def test_detail(self):
        p = Path('/tmp/test')
        self.assertEqual(p.detail, {
            'name': 'test',
            'path': '/tmp/test',
            'parent': '/tmp',
            'url': '%252Ftmp%252Ftest',
            'suffix': '',
            'parts': ('/', 'tmp', 'test')
        })

    def test_exists(self):
        def postive():            
            fs = MagicMock()
            fs_exists = MagicMock(return_value=True)
            fs.exists = fs_exists
            p = Path('/tmp/temp.txt')
            assert p.check_exists(fs) == True
        def negtive():
            fs = MagicMock()
            fs_exists = MagicMock(return_value=False)
            fs.exists = fs_exists
            p = Path('/tmp/temp.txt')
            assert p.check_exists(fs) == False
        postive()
        negtive()

    def test_copy_init(self):
        p = Path('/tmp/file')
        p2 = Path(p)
        assert p.abs == p2.abs        

    def test_div(self):
        p = Path('/tmp')
        p = p / 'sub'
        assert p.abs == '/tmp/sub'

    def test_yaml_dump(self):
        p = Path('/tmp/test')
        import yaml
        assert yaml.dump(p) == "!path '/tmp/test'\n"

    def test_yaml_load(self):
        import yaml
        p = yaml.load("!path '/tmp/test'\n")
        assert p.abs == "/tmp/test"