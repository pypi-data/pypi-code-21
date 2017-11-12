#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import abstractproperty

from cloudshell.devices.flows.cli_action_flows import RunCommandFlow
from cloudshell.devices.runners.interfaces.run_command_runner_interface import RunCommandInterface


class RunCommandRunner(RunCommandInterface):
    def __init__(self, logger):
        """Create RunCommandOperations

        :param logger: QsLogger object
        """
        self._logger = logger

    @abstractproperty
    def cli_handler(self):
        """ CLI Handler property
        :return: CLI handler
        """

        pass

    @property
    def run_command_flow(self):
        return RunCommandFlow(self.cli_handler, self._logger)

    def run_custom_command(self, custom_command):
        """ Execute custom command on device

        :param custom_command: command
        :return: result of command execution
        """

        return self.run_command_flow.execute_flow(custom_command=custom_command)

    def run_custom_config_command(self, custom_command):
        """ Execute custom command in configuration mode on device

        :param custom_command: command
        :return: result of command execution
        """

        return self.run_command_flow.execute_flow(custom_command=custom_command, is_config=True)
