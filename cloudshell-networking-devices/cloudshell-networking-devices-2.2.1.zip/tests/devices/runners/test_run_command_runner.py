import unittest

import mock

from cloudshell.devices.runners.run_command_runner import RunCommandRunner


class TestRunCommandRunner(unittest.TestCase):
    def setUp(self):
        class TestedClass(RunCommandRunner):
            @property
            def cli_handler(self):
                pass

        self.tested_class = TestedClass
        self.logger = mock.MagicMock()
        self.runner = TestedClass(logger=self.logger)

    def test_cli_handler(self):
        """Check that instance can't be instantiated without implementation of the "cli_handler" method"""
        class TestedClass(RunCommandRunner):
            pass

        with self.assertRaisesRegexp(TypeError, "Can't instantiate abstract class TestedClass with "
                                                "abstract methods cli_handler"):
            TestedClass(logger=self.logger)

    @mock.patch("cloudshell.devices.runners.run_command_runner.RunCommandFlow")
    def test_run_custom_command(self, run_command_flow_class):
        """Check that method will execute RunCommandFlow flow without is_config flag"""
        custom_command = "test custom command"
        expected_res = mock.MagicMock()
        run_command_flow = mock.MagicMock(
            execute_flow=mock.MagicMock(
                return_value=expected_res))

        run_command_flow_class.return_value = run_command_flow
        # act
        with mock.patch.object(self.tested_class, "cli_handler") as cli_handler:
            result = self.runner.run_custom_command(custom_command=custom_command)

            # verify
            self.assertEqual(result, expected_res)
            run_command_flow_class.assert_called_once_with(cli_handler, self.logger)
            run_command_flow.execute_flow.assert_called_once_with(custom_command=custom_command)

    @mock.patch("cloudshell.devices.runners.run_command_runner.RunCommandFlow")
    def test_run_custom_config_command(self, run_command_flow_class):
        """Check that method will execute RunCommandFlow flow with is_config flag"""
        custom_command = "test custom command"
        expected_res = mock.MagicMock()
        run_command_flow = mock.MagicMock(
            execute_flow=mock.MagicMock(
                return_value=expected_res))

        run_command_flow_class.return_value = run_command_flow
        # act
        with mock.patch.object(self.tested_class, "cli_handler") as cli_handler:
            result = self.runner.run_custom_config_command(custom_command=custom_command)

            # verify
            self.assertEqual(result, expected_res)
            run_command_flow_class.assert_called_once_with(cli_handler, self.logger)
            run_command_flow.execute_flow.assert_called_once_with(custom_command=custom_command,
                                                                  is_config=True)
