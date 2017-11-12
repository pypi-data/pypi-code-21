import unittest

import mock

from cloudshell.devices import driver_helper


class TestDriverHelper(unittest.TestCase):

    @mock.patch("cloudshell.devices.driver_helper.SessionPoolManager")
    @mock.patch("cloudshell.devices.driver_helper.CLI")
    def test_get_cli(self, cli_class, session_pool_manager_class):
        """Check that method will return CLI instance"""
        cli = mock.MagicMock()
        cli_class.return_value = cli
        session_pool = mock.MagicMock()
        session_pool_manager_class.return_value = session_pool
        session_pool_size = 10
        pool_timeout = 50
        # act
        result = driver_helper.get_cli(session_pool_size=session_pool_size, pool_timeout=pool_timeout)
        # verify
        self.assertEqual(result, cli)
        cli_class.assert_called_once_with(session_pool=session_pool)
        session_pool_manager_class.assert_called_once_with(max_pool_size=session_pool_size,
                                                           pool_timeout=pool_timeout)

    @mock.patch("cloudshell.devices.driver_helper.LoggingSessionContext")
    def test_get_logger_with_thread_id(self, logging_session_context_class):
        """Check that method will use LoggingSessionContext to return child logger with same handlers as main one"""
        context = mock.MagicMock()
        test_handler = mock.MagicMock()
        test_filter = mock.MagicMock()
        logger = mock.MagicMock()
        parent_logger = mock.MagicMock(getChild=mock.MagicMock(return_value=logger),
                                       filters=[test_filter],
                                       handlers=[test_handler])
        logging_session_context_class.get_logger_for_context.return_value = parent_logger
        # act
        result = driver_helper.get_logger_with_thread_id(context=context)
        # verify
        self.assertEqual(result, logger)
        self.assertEqual(logger.level, parent_logger.level)
        logger.addHandler.assert_called_once_with(test_handler)
        logger.addFilter.assert_called_once_with(test_filter)

    @mock.patch("cloudshell.devices.driver_helper.CloudShellSessionContext")
    def test_get_api(self, cloudshell_session_context_class):
        """Check that method will use CloudShellSessionContext to get sesison"""
        context = mock.MagicMock()
        cs_session_context = mock.MagicMock()
        cloudshell_session_context_class.return_value = cs_session_context
        # act
        result = driver_helper.get_api(context=context)
        # verify
        self.assertEqual(result, cs_session_context.get_api())
        cloudshell_session_context_class.assert_called_once_with(context)

    @mock.patch("cloudshell.devices.driver_helper.SNMPV3Parameters")
    def test_get_snmp_parameters_from_command_context_for_snmp_v3(self, snmpv3parameters_class):
        """Check that method will return SNMPV3Parameters instance for snmp_version=v3 in config"""
        config = mock.MagicMock(snmp_version="v3")
        api = mock.MagicMock()
        snmp_v3 = mock.MagicMock()
        snmpv3parameters_class.return_value = snmp_v3
        decrypted_snmp_string = mock.MagicMock()
        api.DecryptPassword.return_value = decrypted_snmp_string
        # act
        result = driver_helper.get_snmp_parameters_from_command_context(resource_config=config, api=api)
        # verify
        self.assertEqual(result, snmp_v3)
        api.DecryptPassword.assert_called_once_with(config.snmp_v3_password)
        snmpv3parameters_class.assert_called_once_with(ip=config.address,
                                                       snmp_user=config.snmp_v3_user,
                                                       snmp_password=api.DecryptPassword().Value,
                                                       snmp_private_key=config.snmp_v3_private_key,
                                                       auth_protocol=config.snmp_v3_auth_protocol,
                                                       private_key_protocol=config.snmp_v3_priv_protocol)

    @mock.patch("cloudshell.devices.driver_helper.SNMPV2WriteParameters")
    def test_get_snmp_parameters_from_command_context_for_snmp_v2_write_community(self, snmpv2parameters_class):
        """Check that method will return SNMPV2Parameters instance for snmp_version=v2 in config"""
        config = mock.MagicMock(snmp_version="v2")
        api = mock.MagicMock()
        snmp_v2 = mock.MagicMock()
        snmpv2parameters_class.return_value = snmp_v2
        decrypted_snmp_string = mock.MagicMock()
        api.DecryptPassword.return_value = decrypted_snmp_string

        # act
        result = driver_helper.get_snmp_parameters_from_command_context(resource_config=config, api=api)

        # verify
        self.assertEqual(result, snmp_v2)
        api.DecryptPassword.assert_called_once_with(config.snmp_write_community)
        snmpv2parameters_class.assert_called_once_with(ip=config.address,
                                                       snmp_write_community=decrypted_snmp_string.Value)

    @mock.patch("cloudshell.devices.driver_helper.SNMPV2ReadParameters")
    def test_get_snmp_parameters_from_command_context_for_snmp_v2_read_community(self, snmpv2parameters_class):
        """Check that method will return SNMPV2ReadParameters instance for snmp_version=v2 in config"""
        config = mock.MagicMock(snmp_version="v2")
        api = mock.MagicMock()
        snmp_v2 = mock.MagicMock()
        snmpv2parameters_class.return_value = snmp_v2
        decrypted_snmp_string = mock.MagicMock()
        test_value = mock.MagicMock()
        test_value.Value = None
        api.DecryptPassword.side_effect = [test_value, decrypted_snmp_string]
        # act
        result = driver_helper.get_snmp_parameters_from_command_context(resource_config=config, api=api)

        # verify
        self.assertEqual(result, snmp_v2)
        snmpv2parameters_class.assert_called_once_with(ip=config.address,
                                                       snmp_read_community=decrypted_snmp_string.Value)

        api.DecryptPassword.assert_called_with(config.snmp_read_community)
        self.assertTrue(api.DecryptPassword.call_count == 2)

    def test_parse_custom_commands(self):
        """Check that method will parse string into list"""
        # act
        result = driver_helper.parse_custom_commands(command="test command1;test command2")
        # verify
        self.assertEqual(result, ["test command1", "test command2"])

    def test_parse_custom_commands_with_empty_command(self):
        """Check that method will return an empty list if command string is empty"""
        # act
        result = driver_helper.parse_custom_commands(command="")
        # verify
        self.assertEqual(result, [])
