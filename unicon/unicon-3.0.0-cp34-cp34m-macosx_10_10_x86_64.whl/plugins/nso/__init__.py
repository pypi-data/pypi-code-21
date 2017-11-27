""" NSO (Network Service Orchestrator) CLI implementation """

__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import time

from unicon.eal.dialogs import Dialog

from unicon.plugins.generic import GenericSingleRpConnection, service_implementation as svc
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from unicon.plugins.nso.settings import NsoSettings
from unicon.plugins.nso.patterns import NsoPatterns
from unicon.plugins.nso.statemachine import NsoStateMachine
from unicon.plugins.nso import service_implementation as nso_svc


class NsoConnectionProvider(GenericSingleRpConnectionProvider):
    """
        Connection provided class for Nso connections.
    """

    def init_handle(self):

        """ Executes the init commands on the device
        """
        con = self.connection
        con._is_connected = True

        con.state_machine.detect_state(con)
        if con.state_machine.current_cli_style == 'cisco':
            exec_commands = con.settings.CISCO_INIT_COMMANDS
            con.state_machine.go_to('cisco_exec',
                                    self.connection.spawn,
                                    context=self.connection.context,
                                    timeout=self.connection.connection_timeout)
        elif con.state_machine.current_cli_style == 'juniper':
            exec_commands = con.settings.JUNIPER_INIT_COMMANDS
            con.state_machine.go_to('juniper_exec',
                                    self.connection.spawn,
                                    context=self.connection.context,
                                    timeout=self.connection.connection_timeout)

        for command in exec_commands:
            con.command(command)


class NsoServiceList:
    """ Nso services. """

    def __init__(self):
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.expect = svc.Expect
        self.expect_log = svc.ExpectLogging
        self.log_user = svc.LogUser
        self.execute = nso_svc.Execute
        self.configure = nso_svc.Configure
        self.cli_style = nso_svc.CliStyle
        self.command = nso_svc.Command


class NsoConnection(GenericSingleRpConnection):
    """
        Connection class for NSO connections.
    """
    os = 'nso'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = NsoStateMachine
    connection_provider_class = NsoConnectionProvider
    subcommand_list = NsoServiceList
    settings = NsoSettings()

