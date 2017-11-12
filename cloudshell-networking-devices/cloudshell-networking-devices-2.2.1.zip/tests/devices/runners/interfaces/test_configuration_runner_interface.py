import unittest

from cloudshell.devices.runners.interfaces.configuration_runner_interface import ConfigurationOperationsInterface


class TestCliCliHandlerInterface(unittest.TestCase):
    def setUp(self):
        class TestedClass(ConfigurationOperationsInterface):
            pass

        self.tested_class = TestedClass

    def test_abstract_methods(self):
        """Check that instance can't be instantiated without implementation of all abstract methods"""
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods orchestration_restore, orchestration_save, "
                                                "restore, save"):
            self.tested_class()
