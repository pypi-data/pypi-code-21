import unittest
from tios import utilities

class TestCheckGromacs514Methods(unittest.TestCase):

    def test_check_gromacs_installed_version(self):
        result = utilities.installed_version('GROMACS')
        self.assertEqual(result, '5.1.4')
