import unittest

from cloudshell.devices.runners.interfaces.connectivity_runner_interface import ConnectivityOperationsInterface


class TestCliCliHandlerInterface(unittest.TestCase):
    def setUp(self):
        class TestedClass(ConnectivityOperationsInterface):
            pass
        self.tested_class = TestedClass

    def test_apply_connectivity_changes(self):
        """Check that instance can't be instantiated without implementation of the 'apply_connectivity_changes'"""
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods apply_connectivity_changes"):
            self.tested_class()
