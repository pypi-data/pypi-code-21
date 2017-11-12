import unittest

from cloudshell.devices.snmp_handler_interface import SnmpHandlerInterface


class TestSnmpHandlerInterface(unittest.TestCase):
    def setUp(self):
        class TestedClass(SnmpHandlerInterface):
            pass
        self.tested_class = TestedClass

    def test_get_snmp_service(self):
        """Check that instance can't be instantiated without implementation of the "get_snmp_service" method"""
        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods get_snmp_service"):
            self.tested_class()
