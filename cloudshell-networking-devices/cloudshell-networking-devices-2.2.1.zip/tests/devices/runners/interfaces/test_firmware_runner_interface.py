import unittest

from cloudshell.devices.runners.interfaces.firmware_runner_interface import FirmwareRunnerInterface


class TestCliCliHandlerInterface(unittest.TestCase):
    def setUp(self):
        class TestedClass(FirmwareRunnerInterface):
            pass
        self.tested_class = TestedClass

    def test_load_firmware(self):
        """Check that instance can't be instantiated without implementation of the "load_firmware" method"""
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods load_firmware"):
            self.tested_class()
