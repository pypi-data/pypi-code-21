import logging
import unittest

from velenxc import func_loading

logging.basicConfig(level=logging.INFO)


class FuncLoadingTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_loading_return_None(self):
        func = func_loading.import_function('r_func_not_exist')

        logging.info(func)
        self.assertTrue(func is None)

    def test_loading_return_function_instance(self):
        func = func_loading.import_function('m_str_to_int')

        logging.info('======== %s', func)
        self.assertTrue(callable(func))

    def test_install_modules(self):
        installed_modules = list(func_loading.install([
            'tests._test_for_func_loading'
        ]))

        logging.info(installed_modules)
        self.assertTrue(len(installed_modules) >= 2)

    def test_install_module(self):
        installed_modules = list(func_loading.install(
            'tests._test_for_func_loading'
        ))

        logging.info(installed_modules)
        self.assertTrue(len(installed_modules) >= 2)

    def test_call_install_function(self):
        func_loading.install([
            'tests._test_for_func_loading'
        ])

        func = func_loading.import_function('f_test_function')

        sequence = [1, 2, 3]

        self.assertEqual(sequence, func(sequence))
