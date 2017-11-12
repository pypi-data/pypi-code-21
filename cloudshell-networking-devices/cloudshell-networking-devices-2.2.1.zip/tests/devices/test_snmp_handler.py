import unittest

import mock

from cloudshell.devices.snmp_handler import SnmpContextManager
from cloudshell.devices.snmp_handler import SnmpHandler


class TestSnmpContextManager(unittest.TestCase):
    def setUp(self):
        self.enable_flow = mock.MagicMock()
        self.disable_flow = mock.MagicMock()
        self.snmp_parameters = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.snmp_cm = SnmpContextManager(enable_flow=self.enable_flow,
                                          disable_flow=self.disable_flow,
                                          snmp_parameters=self.snmp_parameters,
                                          logger=self.logger)

    @mock.patch("cloudshell.devices.snmp_handler.QualiSnmp")
    def test__enter__(self, quali_snmp_class):
        """Check that method will return QualiSnmp instance and execute enable flow"""
        quali_snmp = mock.MagicMock()
        quali_snmp_class.return_value = quali_snmp
        # act
        with self.snmp_cm as snmp:
            pass
        # verify
        self.assertEqual(snmp, quali_snmp)
        quali_snmp_class.assert_called_once_with(self.snmp_parameters, self.logger)
        self.enable_flow.execute_flow.assert_called_once_with(self.snmp_parameters)

    @mock.patch("cloudshell.devices.snmp_handler.QualiSnmp")
    def test__exit__(self, quali_snmp_class):
        """Check that method will execute disable flow"""
        # act
        with self.snmp_cm:
            pass
        # verify
        self.disable_flow.execute_flow.assert_called_once_with(self.snmp_parameters)


class TestSnmpHandler(unittest.TestCase):
    def setUp(self):
        self.resource_conf = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.api = mock.MagicMock()

        class TestedClass(SnmpHandler):
            def _create_enable_flow(self):
                pass

            def _create_disable_flow(self):
                pass

        self.snmp = TestedClass(resource_config=self.resource_conf,
                                logger=self.logger,
                                api=self.api)

    def test_enable_flow(self):
        """Check that method will create enable flow if 'enable_snmp' config is set to True"""
        self.resource_conf.enable_snmp = "True"
        enable_flow = mock.MagicMock()
        self.snmp._create_enable_flow = mock.MagicMock(return_value=enable_flow)
        # act
        result = self.snmp.enable_flow
        # verify
        self.assertEqual(result, enable_flow)

    def test_disable_flow(self):
        """Check that method will create disable flow if 'disable_snmp' config is set to True"""
        self.resource_conf.disable_snmp = "True"
        disable_flow = mock.MagicMock()
        self.snmp._create_disable_flow = mock.MagicMock(return_value=disable_flow)
        # act
        result = self.snmp.disable_flow
        # verify
        self.assertEqual(result, disable_flow)

    def test_create_enable_flow(self):
        """Check that instance can't be instantiated without implementation of the "_create_enable_flow" method"""
        class TestedClass(SnmpHandler):
            def _create_disable_flow(self):
                pass

        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods _create_enable_flow"):
            TestedClass(resource_config=self.resource_conf,
                        logger=self.logger,
                        api=self.api)

    def _create_disable_flow(self):
        """Check that instance can't be instantiated without implementation of the "_create_disable_flow" method"""
        class TestedClass(SnmpHandler):
            def _create_enable_flow(self):
                pass

        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods _create_disable_flow"):
            TestedClass(resource_config=self.resource_conf,
                        logger=self.logger,
                        api=self.api)

    @mock.patch("cloudshell.devices.snmp_handler.SnmpContextManager")
    def test_get_snmp_service(self, snmp_context_manager_class):
        """Check that method will return SnmpContextManager instance"""
        snmp_context_manager = mock.MagicMock()
        snmp_context_manager_class.return_value = snmp_context_manager
        # act
        result = self.snmp.get_snmp_service()
        # verify
        self.assertEqual(result, snmp_context_manager)
        snmp_context_manager_class.assert_called_once_with(self.snmp.enable_flow,
                                                           self.snmp.disable_flow,
                                                           self.snmp._snmp_parameters,
                                                           self.snmp._logger)
