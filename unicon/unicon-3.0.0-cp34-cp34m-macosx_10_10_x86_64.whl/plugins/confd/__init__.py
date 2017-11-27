""" ConfD CLI implementation """

__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import time

from unicon.eal.dialogs import Dialog

from unicon.plugins.generic import GenericSingleRpConnection, service_implementation as svc
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from unicon.plugins.confd.settings import ConfdSettings
from unicon.plugins.confd.patterns import ConfdPatterns
from unicon.plugins.confd.statemachine import ConfdStateMachine
from unicon.plugins.confd import service_implementation as confd_svc

p = ConfdPatterns()


def wait_and_send_yes(spawn):
    time.sleep(0.1)
    spawn.sendline('yes')


class ConfdConnectionProvider(GenericSingleRpConnectionProvider):
    """
        Connection provided class for ConfD connections.
    """
    def get_connection_dialog(self):
        pre_connection_dialogs = Dialog([
            [p.continue_connect,
                wait_and_send_yes,
                None, True, False]
            ])

        connection_dialogs = super().get_connection_dialog() + pre_connection_dialogs

        return connection_dialogs

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
            con.command(command, error_pattern=[])


class ConfdServiceList:
    """ ConfD services. """

    def __init__(self):
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.expect = svc.Expect
        self.expect_log = svc.ExpectLogging
        self.log_user = svc.LogUser
        self.execute = confd_svc.Execute
        self.configure = confd_svc.Configure
        self.cli_style = confd_svc.CliStyle
        self.command = confd_svc.Command


class ConfdConnection(GenericSingleRpConnection):
    """
        Connection class for ConfD connections.
    """
    os = 'confd'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = ConfdStateMachine
    connection_provider_class = ConfdConnectionProvider
    subcommand_list = ConfdServiceList
    settings = ConfdSettings()

