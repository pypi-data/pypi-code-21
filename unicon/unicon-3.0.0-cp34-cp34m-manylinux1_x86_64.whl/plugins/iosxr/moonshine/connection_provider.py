__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Isobel Ormiston <iormisto@cisco.com>"

import time

from random import randint

from unicon.plugins.iosxr.connection_provider \
    import IOSXRSingleRpConnectionProvider, IOSXRDualRpConnectionProvider
from unicon.plugins.iosxr.moonshine.statements import MoonshineStatements
from unicon.plugins.iosxr.moonshine.patterns import MoonshinePatterns
from unicon.plugins.iosxr.errors import RpNotRunningError
from unicon.eal.dialogs import Dialog


patterns = MoonshinePatterns()
iosxr_statements = MoonshineStatements()

class MoonshineSingleRpConnectionProvider(IOSXRSingleRpConnectionProvider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def init_handle(self):
        """ Executes the init commands on the device after bringing
            it to enable state """
        con = self.connection
        con._is_connected = True
        con.state_machine.go_to('enable',
                                self.connection.spawn,
                                context=self.connection.context,
                                timeout=self.connection.connection_timeout)


class MoonshineDualRpConnectionProvider(IOSXRDualRpConnectionProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def init_active(self):
        """ Executes the init commands on the device  """
        con = self.connection
        exec_commands = con.settings.IOSXR_INIT_EXEC_COMMANDS
        for command in exec_commands:
            con.execute(command)
        hostname_command = []
        if con.hostname != None and con.hostname != '':
            hostname_command = ['hostname ' + con.hostname]
        config_commands = con.settings.MOONSHINE_INIT_CONFIG_COMMANDS
        con.configure(hostname_command + config_commands)
