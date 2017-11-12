import unittest

import mock

from cloudshell.devices.flows.action_flows import RunCommandFlow


class TestRunCommandFlow(unittest.TestCase):
    def setUp(self):
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.run_flow = RunCommandFlow(cli_handler=self.cli_handler,
                                       logger=self.logger)

    def test_execute_flow_in_enable_mode(self):
        """Check that method will get CLI session in the enable mode and return response from the device"""
        custom_command = "test command"
        response = "test response"
        session = mock.MagicMock(send_command=mock.MagicMock(return_value=response))
        self.cli_handler.get_cli_service.return_value = mock.MagicMock(__enter__=mock.MagicMock(return_value=session))
        # act
        result = self.run_flow.execute_flow(custom_command=custom_command)
        # verify
        self.assertEqual(result, response)
        self.cli_handler.get_cli_service.assert_called_once_with(self.cli_handler.enable_mode)

    def test_execute_flow_in_config_mode(self):
        """Check that method will get CLI session in the config mode and return response from the device"""
        custom_command = "test command"
        response = "test response"
        session = mock.MagicMock(send_command=mock.MagicMock(return_value=response))
        self.cli_handler.get_cli_service.return_value = mock.MagicMock(__enter__=mock.MagicMock(return_value=session))
        # act
        result = self.run_flow.execute_flow(custom_command=custom_command,
                                            is_config=True)
        # verify
        self.assertEqual(result, response)
        self.cli_handler.get_cli_service.assert_called_once_with(self.cli_handler.config_mode)

    def test_execute_flow_enable_mode_is_none(self):
        """Check that method will raise exception if enable_mode is None"""
        custom_command = "test command"
        self.cli_handler.enable_mode = None
        # act
        with self.assertRaisesRegexp(Exception, "Enable Mode has to be defined"):
            self.run_flow.execute_flow(custom_command=custom_command)

    def test_execute_flow_config_mode_is_none(self):
        """Check that method will raise exception if config_mode is None"""
        custom_command = "test command"
        self.cli_handler.config_mode = None
        # act
        with self.assertRaisesRegexp(Exception, "Config Mode has to be defined"):
            self.run_flow.execute_flow(custom_command=custom_command, is_config=True)
