#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import abstractmethod


# Deprecated, will be removed
class BaseFlow(object):
    def __init__(self, cli_handler, logger):
        self._cli_handler = cli_handler
        self._logger = logger
        self._command_actions = None


class SaveConfigurationFlow(BaseFlow):
    def __init__(self, cli_handler, logger):
        super(SaveConfigurationFlow, self).__init__(cli_handler, logger)

    @abstractmethod
    def execute_flow(self, folder_path, configuration_type, vrf_management_name=None):
        """ Execute flow which save selected file to the provided destination

        :param folder_path: destination path where file will be saved
        :param configuration_type: source file, which will be saved
        :param vrf_management_name: Virtual Routing and Forwarding Name
        :return: saved configuration file name
        """

        pass


class RestoreConfigurationFlow(BaseFlow):
    def __init__(self, cli_handler, logger):
        super(RestoreConfigurationFlow, self).__init__(cli_handler, logger)

    @abstractmethod
    def execute_flow(self, path, restore_method, configuration_type, vrf_management_name):
        """ Execute flow which save selected file to the provided destination

        :param path: the path to the configuration file, including the configuration file name
        :param restore_method: the restore method to use when restoring the configuration file.
                               Possible Values are append and override
        :param configuration_type: the configuration type to restore. Possible values are startup and running
        :param vrf_management_name: Virtual Routing and Forwarding Name
        """

        pass


class AddVlanFlow(BaseFlow):
    def __init__(self, cli_handler, logger):
        super(AddVlanFlow, self).__init__(cli_handler, logger)

    @abstractmethod
    def execute_flow(self, vlan_range, port_mode, port_name, qnq, c_tag):
        """ Configures VLANs on multiple ports or port-channels

        :param vlan_range: VLAN or VLAN range
        :param port_mode: mode which will be configured on port. Possible Values are trunk and access
        :param port_name: full port name
        :param qnq:
        :param c_tag:
        :return:
        """

        pass


class RemoveVlanFlow(BaseFlow):
    def __init__(self, cli_handler, logger):
        super(RemoveVlanFlow, self).__init__(cli_handler, logger)

    @abstractmethod
    def execute_flow(self, vlan_range, port_name, port_mode, action_map=None, error_map=None):
        """ Remove configuration of VLANs on multiple ports or port-channels

        :param vlan_range: VLAN or VLAN range
        :param port_name: full port name
        :param port_mode: mode which will be configured on port. Possible Values are trunk and access
        :param action_map:
        :param error_map:
        :return:
        """

        pass


class LoadFirmwareFlow(BaseFlow):
    def __init__(self, cli_handler, logger):
        super(LoadFirmwareFlow, self).__init__(cli_handler, logger)

    @abstractmethod
    def execute_flow(self, path, vrf, timeout):
        """Load a firmware onto the device

        :param path: The path to the firmware file, including the firmware file name
        :param vrf: Virtual Routing and Forwarding Name
        :param timeout:
        :return:
        """

        pass


class RunCommandFlow(BaseFlow):
    def __init__(self, cli_handler, logger):
        super(RunCommandFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, custom_command="", is_config=False):
        """ Execute flow which run custom command on device

        :param custom_command: the command to execute on device
        :param is_config: if True then run command in configuration mode
        :return: command execution output
        """

        responses = []
        if isinstance(custom_command, str):
            commands = [custom_command]
        elif isinstance(custom_command, tuple):
            commands = list(custom_command)
        else:
            commands = custom_command

        if is_config:
            mode = self._cli_handler.config_mode
            if not mode:
                raise Exception(self.__class__.__name__,
                                "CliHandler configuration is missing. Config Mode has to be defined")
        else:
            mode = self._cli_handler.enable_mode
            if not mode:
                raise Exception(self.__class__.__name__,
                                "CliHandler configuration is missing. Enable Mode has to be defined")

        with self._cli_handler.get_cli_service(mode) as session:
            for cmd in commands:
                responses.append(session.send_command(command=cmd))
        return '\n'.join(responses)
