import unittest

import mock

from cloudshell.devices.runners.state_runner import StateRunner


class TestStateRunner(unittest.TestCase):
    def setUp(self):
        self.logger = mock.MagicMock()
        self.api = mock.MagicMock()
        self.resource_config = mock.MagicMock()

        class TestedStateRunner(StateRunner):
            def cli_handler(self):
                pass

        self.state_runner = TestedStateRunner(logger=self.logger,
                                              api=self.api,
                                              resource_config=self.resource_config)

    def test_abstract_methods(self):
        """Check that instance can't be instantiated without implementation of the all abstract methods"""
        class TestedClass(StateRunner):
            pass

        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods cli_handler"):
            TestedClass(logger=self.logger,
                        api=self.api,
                        resource_config=self.resource_config)

    def test_shutdown(self):
        """Check that method will raise exception"""
        with self.assertRaisesRegexp(Exception, "Shutdown command isn't available for the current device"):
            self.state_runner.shutdown()

    @mock.patch("cloudshell.devices.runners.state_runner.RunCommandFlow")
    def test_health_check_passed(self, run_command_flow_class):
        """Check that method will execute RunCommandFlow and return success message"""
        run_command_flow = mock.MagicMock()
        run_command_flow_class.return_value = run_command_flow
        # act
        result = self.state_runner.health_check()
        # verify
        self.assertEqual(result, "Health check on resource {} passed."
                         .format(self.resource_config.name))

        run_command_flow_class.assert_called_once_with(self.state_runner.cli_handler,
                                                       self.logger)
        run_command_flow.execute_flow.assert_called_once_with()
        self.api.SetResourceLiveStatus.assert_called_once_with(self.resource_config.name,
                                                               "Online",
                                                               result)

    @mock.patch("cloudshell.devices.runners.state_runner.RunCommandFlow")
    def test_health_check_failed(self, run_command_flow_class):
        """Check that method will execute RunCommandFlow and return failed message"""
        run_command_flow = mock.MagicMock(execute_flow=mock.MagicMock(
            side_effect=Exception))
        run_command_flow_class.return_value = run_command_flow
        # act
        result = self.state_runner.health_check()
        # verify
        self.assertEqual(result, "Health check on resource {} failed."
                         .format(self.resource_config.name))
        self.api.SetResourceLiveStatus.assert_called_once_with(self.resource_config.name,
                                                               "Error",
                                                               result)

    @mock.patch("cloudshell.devices.runners.state_runner.RunCommandFlow")
    def test_health_check_failed_to_update_live_status(self, run_command_flow_class):
        """Check that method will handle """
        self.api.SetResourceLiveStatus.side_effect = Exception()
        # act
        result = self.state_runner.health_check()
        # verify
        self.assertEqual(result, "Health check on resource {} passed."
                         .format(self.resource_config.name))
