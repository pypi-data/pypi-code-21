import unittest
from dxpy.configs.base import Configs


class TestConfigs(unittest.TestCase):
    def test_basic(self):
        class ConfigsA(Configs):
            _names = ('name1', 'name2')
            default_configs = {'name1': 'value1'}

        a = ConfigsA()
        self.assertEqual(a['name1'], 'value1')

    

