__version__ = "2.1.1"

# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest
import imp
import os

def attempt_import(module):
        try:                       
                imp.find_module(module)
                return 1
        except:
                return 0
        
class suite(unittest.TestCase):
	def test_base_case(self):
                #Base Case Tests
                self.assertEqual(True, True)

	def test_imports(self):
                #Import Tests
                self.assertEqual(attempt_import('numpy'), 1)
                self.assertEqual(attempt_import('scipy'), 1)
                self.assertEqual(attempt_import('matplotlib'), 1)
                self.assertEqual(attempt_import('igraph'), 1)
                self.assertEqual(attempt_import('pysam'), 1)
                self.assertEqual(attempt_import('PIL'), 1)
                self.assertEqual(attempt_import('patsy'), 1)
                self.assertEqual(attempt_import('pandas'), 1)
                self.assertEqual(attempt_import('wx'), 1)

        def test_version_verify(self):
                import altanalyze_test
                self.assertEqual(altanalyze_test.__version__, "2.1.1")

        def test_package_data_included(self):
                self.assertEqual(os.path.isdir("altanalyze/Config"), True)
                self.assertEqual(os.path.isdir("altanalyze/AltDatabase"), True)
                self.assertEqual(os.path.isdir("altanalyze/Documentation"), True)

def test_success():
	from altanalyze_test import tests
	loader = unittest.TestLoader()
	suite = loader.loadTestsFromModule(tests)
	return suite
