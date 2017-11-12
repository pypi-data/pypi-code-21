import unittest

from cloudshell.devices.runners.interfaces.run_command_runner_interface import RunCommandInterface


class TestCliCliHandlerInterface(unittest.TestCase):
    def setUp(self):
        class TestedClass(RunCommandInterface):
            pass
        self.tested_class = TestedClass

    def test_abstract_methods(self):
        """Check that instance can't be instantiated without implementation of all abstract methods"""
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods run_custom_command, run_custom_config_command"):
            self.tested_class()
