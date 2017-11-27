__copyright__ = "# Copyright (c) 2016 by cisco Systems, Inc. All rights reserved."
__author__ = "Syed Raza <syedraza@cisco.com>"

import time

from random import randint

from unicon.bases.routers.connection_provider \
    import BaseSingleRpConnectionProvider, BaseDualRpConnectionProvider
from unicon.plugins.iosxr.statements import IOSXRStatements
from unicon.plugins.iosxr.patterns import IOSXRPatterns
from unicon.plugins.iosxr.errors import RpNotRunningError
from unicon.eal.dialogs import Dialog
from unicon.bases.routers.connection_provider \
    import BaseDualRpConnectionProvider

from unicon.bases.connection import DEFAULT_LEARNED_HOSTNAME

patterns = IOSXRPatterns()
iosxr_statements = IOSXRStatements()

pre_connection_statement_list = [
    iosxr_statements.escape_char_stmt,
    iosxr_statements.press_return_stmt,
    iosxr_statements.continue_connect_stmt,
    iosxr_statements.connection_refused_stmt,
    iosxr_statements.disconnect_error_stmt ]
authentication_statement_list = [iosxr_statements.bad_password_stmt,
    iosxr_statements.login_incorrect,
    iosxr_statements.login_stmt,
    iosxr_statements.useraccess_stmt,
    iosxr_statements.password_stmt]


class IOSXRSingleRpConnectionProvider(BaseSingleRpConnectionProvider):

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
        exec_commands = con.settings.IOSXR_INIT_EXEC_COMMANDS
        for command in exec_commands:
            con.execute(command)
        hostname_command = []
        if con.hostname != None and con.hostname != '':
            hostname_command = ['hostname ' + con.hostname]
        config_commands = con.settings.IOSXR_INIT_CONFIG_COMMANDS
        con.configure(hostname_command + config_commands)

    def get_connection_dialog(self):
        connection_statement_list = authentication_statement_list + \
            pre_connection_statement_list
        return Dialog(connection_statement_list)


class IOSXRDualRpConnectionProvider(BaseDualRpConnectionProvider):

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
        config_commands = con.settings.IOSXR_INIT_CONFIG_COMMANDS
        con.configure(hostname_command + config_commands)

    def get_connection_dialog(self):
        connection_statement_list = authentication_statement_list + \
            pre_connection_statement_list
        return Dialog(connection_statement_list)

    def designate_handles(self):
        """ Identifies the Role of each handle and designates if it is active or
            standby and bring the active RP to enable state """
        con = self.connection
        if con.a.state_machine.current_state is 'standby_locked':
            target_rp = 'b'
            other_rp = 'a'
        elif con.b.state_machine.current_state is 'standby_locked':
            target_rp = 'a'
            other_rp = 'b'
        else:
            con.log.info("None of the RPs are currently in standby locked state")
            target_rp = 'a'
            other_rp = 'b'
        target_handle = getattr(con, target_rp)
        other_handle = getattr(con, other_rp)
        target_handle.role = 'active'
        other_handle.role = 'standby'
        target_handle.state_machine.go_to('enable',
                                          target_handle.spawn,
                                          context=con.context,
                                          timeout=con.connection_timeout,
                                          dialog=self.get_connection_dialog(),
                                          )
        con._handles_designated = True

    def connect(self):
        """ Connects, initializes and designates handle """
        con = self.connection
        con.log.info('+++ connection to %s +++' % str(self.connection.a.spawn))
        con.log.info('+++ connection to %s +++' % str(self.connection.b.spawn))
        self.establish_connection()
        con.log.info('+++ designating handles +++')
        self.designate_handles()
        con.log.info('+++ initializing active handle +++')
        self.init_active()
        self.connection._is_connected = True


class IOSXRVirtualConnectionProviderLaunchWaiter(object):
    """ This class is meant to be multiply inherited along with the
    appropriate connection provider base class.
    """

    def wait_for_launch_complete(self,
            initial_discovery_wait_sec, initial_wait_sec, post_prompt_wait_sec,
            connection, log, hostname, checkpoint_pattern,
            learn_hostname=False):
        con = connection
        # Checking if a device is launching or not
        log.info('\nTrying to connect to prompt on device {} ...'.\
            format(hostname))
        spwn = connection.spawn

        initial_prompts = [
            patterns.enable_prompt.replace('%N',
                DEFAULT_LEARNED_HOSTNAME if learn_hostname else hostname),
            patterns.config_prompt.replace('%N',
                DEFAULT_LEARNED_HOSTNAME if learn_hostname else hostname),
            patterns.username_prompt,
            patterns.password_prompt,
            patterns.standby_prompt,
            patterns.logout_prompt ]
        #result = None
        spwn.send('\r')
        time.sleep(initial_discovery_wait_sec)
        spwn.read_update_buffer()

        # Had to sleep/read twice in order to connect to iosxrv-ha
        time.sleep(initial_discovery_wait_sec)
        spwn.read_update_buffer()
        result = spwn.match_buffer(initial_prompts)
        if result is False:
            log.info("Can not access prompt on device {} so assuming "
                " virtual launch is in progress ...".\
                format(hostname))
            spwn.expect([checkpoint_pattern, patterns.standby_prompt],
                timeout=initial_wait_sec, trim_buffer=False)
            log.info("Final steps in launching virtual device {} detected: "
                "will attempt to access prompt in ~{} seconds.".\
                format(hostname, post_prompt_wait_sec))
            # Random timer to display prompts from different routers with a
            # slight delay from each other
            time.sleep(post_prompt_wait_sec - 10 + randint(10, 30))

