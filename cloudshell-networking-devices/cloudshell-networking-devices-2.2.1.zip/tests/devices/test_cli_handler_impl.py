import unittest

import mock

from cloudshell.devices.cli_handler_impl import CliHandlerImpl


class TestCliHandlerImpl(unittest.TestCase):
    def setUp(self):
        self.cli = mock.MagicMock()
        self.config = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.api = mock.MagicMock()

        class TestedClass(CliHandlerImpl):
            enable_mode = ""
            config_mode = ""

        self.cli_handler = TestedClass(cli=self.cli,
                                       resource_config=self.config,
                                       logger=self.logger,
                                       api=self.api)



        self.tested_class = TestedClass

    def test_abstract_methods(self):
        """Check that instance can't be instantiated without implementation of all abstract methods"""
        class TestedClass(CliHandlerImpl):
            pass

        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods config_mode, enable_mode"):
            TestedClass(cli=self.cli,
                        resource_config=self.config,
                        logger=self.logger,
                        api=self.api)

    def test_username(self):
        """Check "username" property"""
        # act
        result = self.cli_handler.username
        # verify
        self.assertEqual(result, self.config.user)

    def test_password(self):
        """Check "password" property"""
        decrypted_pass = mock.MagicMock()
        self.api.DecryptPassword.return_value = decrypted_pass
        # act
        result = self.cli_handler.password
        # verify
        self.assertEqual(result, decrypted_pass.Value)
        self.api.DecryptPassword.assert_called_once_with(self.config.password)

    def test_resource_address(self):
        """Check "resource_address" property"""
        # act
        result = self.cli_handler.resource_address
        # verify
        self.assertEqual(result, self.config.address)

    def test_port(self):
        """Check "port" property"""
        # act
        result = self.cli_handler.port
        # verify
        self.assertEqual(result, self.config.cli_tcp_port)

    def test_cli_type(self):
        """Check "cli_type" property"""
        # act
        result = self.cli_handler.cli_type
        # verify
        self.assertEqual(result, self.config.cli_connection_type)

    @mock.patch("cloudshell.devices.cli_handler_impl.SSHSession")
    def test_ssh_session(self, ssh_session_class):
        """Check that method will return SSHSession instance"""
        ssh_session = mock.MagicMock()
        ssh_session_class.return_value = ssh_session
        # act
        result = self.cli_handler._ssh_session()
        # verify
        self.assertEqual(result, ssh_session)
        ssh_session_class.assert_called_once_with(self.cli_handler.resource_address,
                                                  self.cli_handler.username,
                                                  self.cli_handler.password,
                                                  self.cli_handler.port,
                                                  self.cli_handler.on_session_start)

    @mock.patch("cloudshell.devices.cli_handler_impl.TelnetSession")
    def test_telnet_session(self, telnet_session_class):
        telnet_session = mock.MagicMock()
        telnet_session_class.return_value = telnet_session
        # act
        result = self.cli_handler._telnet_session()
        # verify
        self.assertEqual(result, telnet_session)
        telnet_session_class.assert_called_once_with(self.cli_handler.resource_address,
                                                     self.cli_handler.username,
                                                     self.cli_handler.password,
                                                     self.cli_handler.port,
                                                     self.cli_handler.on_session_start)

    def test_new_sessions_returns_ssh_session(self):
        """Check that method will return SSH session if cli_type is 'ssh'"""
        ssh_session = mock.MagicMock()
        self.cli_handler._ssh_session = mock.MagicMock(return_value=ssh_session)
        self.config.cli_connection_type = "SSH"
        # act
        result = self.cli_handler._new_sessions()
        # verify
        self.assertEqual(result, ssh_session)

    def test_new_sessions_returns_telnet_session(self):
        """Check that method will return Telnet session if cli_type is 'telnet'"""
        telnet_session = mock.MagicMock()
        self.cli_handler._telnet_session = mock.MagicMock(return_value=telnet_session)
        self.config.cli_connection_type = "TELNET"
        # act
        result = self.cli_handler._new_sessions()
        # verify
        self.assertEqual(result, telnet_session)

    def test_new_sessions_returns_telnet_and_ssh_sessions(self):
        """Check that method will return list with SSH and Telnet sessions"""
        ssh_session = mock.MagicMock()
        telnet_session = mock.MagicMock()
        self.cli_handler._ssh_session = mock.MagicMock(return_value=ssh_session)
        self.cli_handler._telnet_session = mock.MagicMock(return_value=telnet_session)
        self.config.cli_connection_type = "auto"
        # act
        result = self.cli_handler._new_sessions()
        # verify
        self.assertEqual(result, [ssh_session, telnet_session])

    def test_get_cli_service(self):
        """Check that method will use get_session for getting CLI session"""
        mode = mock.MagicMock()
        session = mock.MagicMock()
        self.cli_handler._new_sessions = mock.MagicMock()
        self.cli_handler._cli.get_session.return_value = session
        # act
        result = self.cli_handler.get_cli_service(command_mode=mode)
        # verify
        self.assertEqual(result, session)
        self.cli_handler._cli.get_session.assert_called_once_with(self.cli_handler._new_sessions(),
                                                                  mode,
                                                                  self.cli_handler._logger)
