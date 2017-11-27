__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Syed Raza <syedraza@cisco.com>"

from unicon.plugins.iosxr.connection_provider import IOSXRSingleRpConnectionProvider
from unicon.plugins.iosxr.statements import IOSXRStatements
from unicon.plugins.iosxr.iosxrv9k.patterns import IOSXRV9KPatterns
from unicon.plugins.iosxr.errors import RpNotRunningError
from unicon.eal.dialogs import Dialog
from random import randint
import time, re

from unicon.plugins.iosxr.connection_provider \
    import IOSXRVirtualConnectionProviderLaunchWaiter

patterns = IOSXRV9KPatterns()
ACTIVE_RP_STATE = 'RUNNING'
  
def check_platform(connection_provider):
    con = connection_provider.connection
    running = False
    loop_counter = 0
    con.log.info('\nChecking show controller dpc rm dpa to ensure all ' \
        'RP/LC are in RUNNING state')
    while loop_counter < 15:
        running = True
        output = con.execute('show controller dpc rm dpa')
        output = output.split('\n')
        for line in output:
            match = re.match(patterns.rp_extract_status, line, re.I)
            if not match:
                continue
            status = match.group(1)
            if status != ACTIVE_RP_STATE:
                running = False
                break
        if running == True or loop_counter == 14:
            break
        loop_counter += 1
        time.sleep(50)
    if running == False:
        con.log.info('RP/LC not in "RUNNING" state')
        raise RpNotRunningError()
    con.log.info("RP/LC in 'RUNNING' state")


class IOSXRV9KSingleRpConnectionProvider(
    IOSXRSingleRpConnectionProvider,
    IOSXRVirtualConnectionProviderLaunchWaiter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def init_handle(self):
        """ Executes the init commands on the device
         after bringing to enable state
        """
        con = self.connection
        con._is_connected = True
        con.state_machine.go_to('enable',
                                self.connection.spawn,
                                context=self.connection.context,
                                timeout=self.connection.connection_timeout)
        check_platform(self)
        exec_commands = con.settings.IOSXR_INIT_EXEC_COMMANDS
        for command in exec_commands:
            con.execute(command)
        hostname_command = []
        if con.hostname != None and con.hostname != '':
            hostname_command = ['hostname ' + con.hostname]
        config_commands = con.settings.IOSXR_INIT_CONFIG_COMMANDS
        con.configure(hostname_command + config_commands)


    def establish_connection(self):
        con = self.connection
        settings = con.settings

        self.wait_for_launch_complete(
            initial_discovery_wait_sec = \
                settings.INITIAL_LAUNCH_DISCOVERY_WAIT_SEC,
            initial_wait_sec = settings.INITIAL_LAUNCH_WAIT_SEC,
            post_prompt_wait_sec = settings.POST_PROMPT_WAIT_SEC,
            connection = con, log=con.log, hostname=con.hostname,
            checkpoint_pattern=patterns.logout_prompt)
        super().establish_connection()

"""
class IOSXRV9KDoubleRpConnectionProvider(IOSXRDoubleRpConnectionProvider):
    pass
"""
