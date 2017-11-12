import unittest

import mock

from cloudshell.devices.flows.snmp_action_flows import BaseSnmpFlow


class TestBaseSnmpFlow(unittest.TestCase):
    def test_init(self):
        """Check that __init__ method will set up object with correct params"""
        snmp_handler = mock.MagicMock()
        logger = mock.MagicMock()
        # act
        snmp_flow = BaseSnmpFlow(snmp_handler=snmp_handler, logger=logger)
        # verify
        self.assertEqual(snmp_flow._snmp_handler, snmp_handler)
        self.assertEqual(snmp_flow._logger, logger)
