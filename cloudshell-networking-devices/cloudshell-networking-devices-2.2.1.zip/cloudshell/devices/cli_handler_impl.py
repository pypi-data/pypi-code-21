#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import abstractproperty

from cloudshell.cli.cli import CLI
from cloudshell.cli.cli_service_impl import CommandModeContextManager
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.devices.cli_handler_interface import CliHandlerInterface


class CliHandlerImpl(CliHandlerInterface):
    def __init__(self, cli, resource_config, logger, api):
        """
        Helps to create cli handler
        :param cli:
        :type cli: CLI
        :param context:
        :param logger:
        :param api:
        :return:
        """

        self._cli = cli
        self.resource_config = resource_config
        self._logger = logger
        self._api = api
        self._password = None

    @abstractproperty
    def enable_mode(self):
        """Define Default Command Mode

        :return: Default Command Mode
        :rtype: CommandMode
        """

        pass

    @abstractproperty
    def config_mode(self):
        """Define Config Command Mode

        :return: Config Command Mode
        :rtype: CommandMode
        """

        pass

    @property
    def username(self):
        return self.resource_config.user

    @property
    def password(self):
        if not self._password:
            password = self.resource_config.password
            self._password = self._api.DecryptPassword(password).Value
        return self._password

    @property
    def resource_address(self):
        """Resource IP

        :return:
        """
        return self.resource_config.address

    @property
    def port(self):
        """Connection port property, to open socket on

        :return:
        """
        return self.resource_config.cli_tcp_port

    @property
    def cli_type(self):
        """Connection type property [ssh|telnet|console|auto]

        :return:
        """
        return self.resource_config.cli_connection_type

    def on_session_start(self, session, logger):
        """Perform some default commands when session just opened (like 'no logging console')

        :param session:
        :param logger:
        :return:
        """
        pass

    def _ssh_session(self):
        return SSHSession(self.resource_address, self.username, self.password, self.port, self.on_session_start)

    def _telnet_session(self):
        return TelnetSession(self.resource_address, self.username, self.password, self.port, self.on_session_start)

    def _new_sessions(self):
        if self.cli_type.lower() == SSHSession.SESSION_TYPE.lower():
            new_sessions = self._ssh_session()
        elif self.cli_type.lower() == TelnetSession.SESSION_TYPE.lower():
            new_sessions = self._telnet_session()
        else:
            new_sessions = [self._ssh_session(), self._telnet_session()]
        return new_sessions

    def get_cli_service(self, command_mode):
        """Use cli.get_session to open CLI connection and switch into required mode

        :param CommandMode command_mode: operation mode, can be default_mode/enable_mode/config_mode/etc.
        :return: created session in provided mode
        :rtype: CommandModeContextManager
        """
        return self._cli.get_session(self._new_sessions(), command_mode, self._logger)
