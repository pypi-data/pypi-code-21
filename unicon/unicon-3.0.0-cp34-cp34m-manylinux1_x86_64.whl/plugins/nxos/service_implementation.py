"""
Module:
    unicon.plugins.generic

Authors:
    ATS TEAM (ats-dev@cisco.com, CSG( STEP) - India)

Description:
    This subpackage implements services specific to NXOS

"""

import re
import collections
from time import sleep

from unicon.bases.routers.services import BaseService
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Dialog
from unicon.plugins.generic.service_implementation import \
    HAReloadService as GenericHAReload
from unicon.plugins.generic.service_implementation import \
    Reload as GenericReload
from unicon.plugins.generic.service_implementation import \
    GetMode as GenericGetMode
from unicon.plugins.generic.service_implementation import \
    GetRPState as GenericGetRPState
from unicon.plugins.generic.service_implementation import \
    SwitchoverService as GenericSwitchover
from unicon.plugins.generic.service_statements import ping6_statement_list, \
    switchover_statement_list, standby_reset_rp_statement_list
from unicon.plugins.generic.service_statements import send_response
from unicon.plugins.nxos.service_statements import nxos_reload_statement_list, \
    ha_nxos_reload_statement_list
from unicon.settings import Settings
from unicon.utils import AttributeDict
from .patterns import NxosPatterns

from .utils import NxosUtils

patterns = NxosPatterns()
settings = Settings()
utils = NxosUtils()


class Reload(GenericReload):
    """ Service to reload the device.

    Arguments:
        reload_command: reload command to be issued on device.
            default reload_command is "reload"
        dialog: Dialog which include list of Statements for
            additional dialogs prompted by reload command, in-case
            it is not in the current list.
        timeout: Timeout value in sec, Default Value is 400 sec

    Returns:
        bool: True on success False otherwise

    Raises:
        SubCommandFailure: on failure.

    Example:
        .. code-block:: python

            rtr.reload()
            # If reload command is other than 'reload'
            rtr.reload(reload_command="reload location all", timeout=400)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.dialog = Dialog(nxos_reload_statement_list)
        self.service_name = 'reload'
        self.timeout = connection.settings.RELOAD_TIMEOUT
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.command = 'reload'
        self.__dict__.update(kwargs)

    def call_service(self,
                     reload_command='reload',
                     dialog=Dialog([]),
                     timeout=400,
                     *args, **kwargs):
        con = self.connection
        timeout = timeout or con.settings.RELOAD_TIMEOUT
        con.log.debug("+++ reloading  %s  with reload_command %s "
                      "and timeout is %s +++"
                      % (self.connection.hostname, reload_command, timeout))
        con.state_machine.go_to(self.end_state,
                                con.spawn,
                                prompt_recovery=self.prompt_recovery,
                                context=self.context)
        if not isinstance(dialog, Dialog):
            raise SubCommandFailure(
                "dialog passed must be an instance of Dialog")
        dialog = dialog
        dialog += Dialog(nxos_reload_statement_list)
        con.spawn.sendline(reload_command)

        try:
            dialog.process(con.spawn,
                           context=self.context,
                           prompt_recovery=self.prompt_recovery,
                           timeout=timeout)
            counter = 3
            while(counter < 3):
                counter = counter + 1
                try:
                    con.state_machine.go_to('any',
                                            con.spawn,
                                            prompt_recovery=self.prompt_recovery,
                                            context=self.context)
                    break
                except Exception as err:
                    if counter >= 3:
                        raise Exception(' Bringing device failed even after retries') from err
                    con.log.info('Retry in process')
                    con.spawn.sendline()
        except Exception as err:
            raise SubCommandFailure("Reload failed : %s" % err)
        #con.state_machine.get_state(self.end_state)
        con.disconnect()
        sleep(10)
        con.connect()
        con.log.debug("+++ Reload Completed Successfully +++")
        self.result = True


class Ping6(BaseService):
    """
      Generic ping6 subcommand

    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.service_name = 'ping6'
        self.timeout = 60
        self.dialog = Dialog(ping6_statement_list)
        self.result = None

        # Ping error Patterns
        self.error_pattern = ['^.*(% )?DSCP.*does not match any topology',
                              'Bad IP (A|a)ddress', 'Ping transmit failed',
                              'Invalid vrf', 'Unable to find',
                              'No Route to Host.*',
                              'Destination Host Unreachable',
                              'Unable to initialize Windows Socket Interface',
                              'IP routing table .* does not exist',
                              'Invalid input',
                              'bad context', 'Failed to resolve',
                              '(U|u)nknown (H|h)ost',
                              'Success rate is 0 percent',
                              '100.00% packet loss',
                              '100 % packat loss']

        # add the keyword arguments to the object
        self.__dict__.update(kwargs)

    def call_service(self, *args, **kwargs):
        con = self.connection

        # Ping Options
        ping_options = ['multicast', 'transport', 'mask', 'vcid', 'tunnel',
                        'dest_start', 'dest_end', 'exp', 'pad', 'ttl',
                        'reply_mode', 'dscp', 'proto', 'count', 'size',
                        'verbose', 'interval', 'timeout_limit',
                        'send_interval', 'vrf', 'src_route_type',
                        'src_route_addr', 'extended_verbose', 'topo',
                        'validate_reply_data', 'force_exp_null_label',
                        'lsp_ping_trace_rev', 'oif', 'tos', 'data_pat',
                        'int', 'udp', 'precedence', 'novell_type',
                        'extended_timeout_limit', 'sweep_min', 'sweep_max',
                        'sweep_interval', 'src_addr', 'df_bit',
                        'ipv6_ext_headers', 'ipv6_hbh_headers',
                        'ipv6_dst_headers', 'ping_packet_timeout',
                        'sweep_ping', 'timestamp_count', 'record_hops',
                        'ping_failures', 'extd_ping', 'addr'
                        ]

        # Default value setting
        ping_context = AttributeDict({})
        for a in ping_options:
            if a is "novell_type":
                ping_context[a] = "\r"
            elif a is "sweep_ping":
                ping_context[a] = "n"
            elif a is 'extd_ping':
                ping_context[a] = "n"
            else:
                ping_context[a] = ""

        # Read input values passed
        # Stringify values in case they are passed as objects.
        for key in kwargs:
            ping_context[key] = str(kwargs[key])

        # Validate Inputs
        if ping_context['addr'] is "":
            if args[0]:
                # Stringify address in case it is passed as an object.
                ping_context['addr'] = str(args[0])
            else:
                raise SubCommandFailure("Address is not specified ")

        if ping_context['src_route_type'] is not "":
            if ping_context['src_route_addr'] in "":
                raise SubCommandFailure(
                    "If src route type is set, then src route addr is mandatory \n")
        elif ping_context['src_route_addr'] is not "":
            raise SubCommandFailure(
                "If src route addr is set, then src route type is mandatory \n")

        timeout = self.timeout
        ping_str = 'ping6' + " " + ping_context['addr']

        # Arguments that need to pass to ping6 command on device.
        # Sequence matters for ping6 command.
        # Key is unicon ping6 service arguments.
        # Value is device ping6 arguments. Prepend and append whitespace.
        ping_seq = collections.OrderedDict()
        ping_seq['multicast'] = ' multicast '
        ping_seq['int'] = ' interface '
        ping_seq['src_addr'] = ' source '
        ping_seq['count'] = ' count '
        ping_seq['send_interval'] = ' interval '
        ping_seq['size'] = ' packet-size '
        ping_seq['vrf'] = ' vrf '

        for unicon_arg, ping6_arg in ping_seq.items():
            if ping_context[unicon_arg]:
                ping_str = ping_str + ping6_arg + ping_context[unicon_arg]

        dialog = self.service_dialog(service_dialog=self.dialog)

        con.spawn.sendline(ping_str)
        try:
            self.result = dialog.process(con.spawn,
                                         context=ping_context,
                                         timeout=timeout)
        except Exception as err:
            raise SubCommandFailure("Ping6 failed", err)
        con.state_machine.go_to(self.end_state, con.spawn,
                                context=self.context)
        self.result = self.result.match_output
        if self.result.rfind(self.connection.hostname):
            self.result = self.result[
                          :self.result.rfind(self.connection.hostname)]


class GetRPState(GenericGetRPState):
    """ Get Rp state

    Service to get the redundancy state of the device rp.
    Returns  standby rp state if standby is passed as input.

    Arguments:
        target: Service target, by default active

    Returns:
        Expected return values are ACTIVE, STANDBY COLD, STANDBY HOT
        raise SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.get_rp_state()
            rtr.get_rp_state(target='standby')
    """
    def call_service(self,
                     target='active',
                     timeout=None,
                     utils=utils,
                     *args,
                     **kwargs):

        """send the command on the right rp and return the output"""
        super().call_service(
            target = target,
            timeout = timeout,
            utils = utils,
            *args,
            **kwargs)

class GetMode(GenericGetMode):
    """ Service to get the redundancy mode of the device.

    Returns:
        'sso', 'rpr' or raise SubCommandFailure on failure.

    Example ::
        .. code-block:: python

            rtr.get_mode()
    """

    def call_service(self,
                     target='active',
                     timeout=None,
                     utils=utils,
                     *args,
                     **kwargs):

        super().call_service(
            target = target,
            timeout = timeout,
            utils = utils,
            *args,
            **kwargs)



class HANxosReloadService(GenericHAReload):
    """ Service to reload the device.


        :arg : reload_command : reload command to be issued on device.
               default reload_command is "reload"

               dialog : Dialog which include list of Statements for
                        additional dialogs prompted by reload command, in-case
                        it is not in the current list.

               timeout : Timeout value in sec, Default Value is 600 sec

        :return : True on Success
                  raise SubCommandFailure on failure.

        Example ::

                  rtr.reload()
                  # If reload command is other than 'reload'
                  rtr.reload(reload_command="reload location all", timeout=700)

    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.result = None
        self.service_name = 'reload'
        self.timeout = connection.settings.HA_RELOAD_TIMEOUT
        self.dialog = Dialog(ha_nxos_reload_statement_list)
        self.command = 'reload'
        self.__dict__.update(kwargs)

    def call_service(self, reload_command='reload',
                     dialog=Dialog([]),
                     target='active',
                     timeout=None,
                     *args,
                     **kwargs):

        """send the command on the right rp and return the output"""
        # create an alias for connection.
        con = self.connection
        timeout = timeout or self.timeout
        # TODO counter value must be defined settings
        counter = 0
        config_retry = 0
        state_machine = self.connection.active.state_machine
        con.log.debug(
            "+++ reloading  %s  with reload_command %s and timeout is %s +++"
            % (con.hostname, reload_command, timeout))

        dialog = self.service_dialog(handle=con.active,
                                     service_dialog=self.dialog)

        state_machine.go_to('enable',
                            con.active.spawn,
                            prompt_recovery=self.prompt_recovery,
                            context=self.context)
        # Issue reload command
        con.active.spawn.sendline(reload_command)
        try:
            dialog.process(con.active.spawn,
                           context=self.context,
                           prompt_recovery=self.prompt_recovery,
                           timeout=timeout)
            con.log.debug("Waiting for HA Config Sync to complete")
            sleep(100)
            counter = 3
            while(counter < 3):
                counter = counter + 1
                try:
                    state_machine.go_to('any',
                                        con.active.spawn,
                                        context=self.context,
                                        timeout=100,
                                        prompt_recovery=self.prompt_recovery,
                                        dialog=con.connection_provider.get_connection_dialog())
                    break
                except Exception as err:
                    if counter >= 3:
                        raise Exception(' Bringing device failed even after retries') from err
                    con.log.info('Retry in process')

                    con.active.spawn.sendline()
                # con.active.state_machine.go_to('any', con.active.spawn, context=self.context)

        except Exception as err:
            raise SubCommandFailure("Reload failed : %s" % err)

        # Issue init commands to disable console logging
        exec_commands = self.connection.settings.HA_INIT_EXEC_COMMANDS
        for command in exec_commands:
            con.execute(command)
        config_commands = self.connection.settings.HA_INIT_CONFIG_COMMANDS
        while config_retry < 15:
            try:
                con.configure(config_commands)
            except Exception as err:
                if re.search("Config mode cannot be entered during Standby \
                             initialization", str(err)):
                    sleep(2)
                    config_retry += 1
            else:
                config_retry = 16
        while counter < 31:
            rp_state = con.get_rp_state(target='standby', timeout=30)
            if rp_state.find('STANDBY HOT') != "-1":
                counter = 32
            else:
                sleep(6)
                counter += 1
        # Stabilise the standby handle
        con.disconnect()
        sleep(10)
        con.connect()
        con.log.debug("+++ Reload Completed Successfully +++")
        self.result = True


class NxosSwitchoverService(GenericSwitchover):
    """ Service to switchover the device.


        :arg : command : command to be issued on device to switchover.
               default command is "redundancy force-switchover"

               dialog : Dialog which include list of Statements for
                        additional dialogs prompted by switchover command,
                        in-case it is not in the current list.

               timeout : Timeout value in sec, Default Value is 500 sec

        :return : True on Success
                  raise SubCommandFailure on failure.

        Example ::

                  rtr.switchover()

                  # If switchover command is other than 'redundancy force-switchover'
                  rtr.switchover(command="command which invoke switchover",
                             timeout=700)

    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.result = None
        self.service_name = 'switchover'
        self.timeout = connection.settings.SWITCHOVER_TIMEOUT
        self.dialog = Dialog(switchover_statement_list)
        self.command = 'system switchover'
        self.__dict__.update(kwargs)

    def call_service(self, command='system switchover',
                     reply=Dialog([]),
                     timeout=None,
                     sync_standby=True,
                     *args,
                     **kwargs):
        # create an alias for connection.
        con = self.connection
        timeout = timeout or self.timeout
        switchover_counter = con.settings.SWITCHOVER_COUNTER
        con.log.debug("+++ Issuing switchover on  %s  with "
                      "switchover_command %s and timeout is %s +++"
                      % (con.hostname, command, timeout))

        # Check is switchover possible?
        rp_state = con.get_rp_state(target='standby', timeout=100)
        if rp_state.find('STANDBY HOT') == "-1":
            raise SubCommandFailure(
                "Switchover can't be issued in %s state" % rp_state)

        # Save current active and standby handle details
        standby_start_cmd = con.standby.start
        # Bring Standby to enable state
        con.enable(target='standby')
        dialog = self.service_dialog(handle=con.active,
                                     service_dialog=self.dialog)
        # Issue switchover command
        con.active.spawn.sendline(command)
        try:
            dialog.process(con.active.spawn,
                           context=self.context,
                           prompt_recovery=self.prompt_recovery,
                           timeout=100)
        except TimeoutError:
            pass
        except SubCommandFailure as err:
            raise SubCommandFailure("Switchover Failed %s" % str(err))

        # Initialise Standby
        try:
            con.standby.spawn.sendline("\r")
            con.standby.spawn.expect(".*")
            con.swap_roles()
            con.active.state_machine.go_to('any',
                                           con.active.spawn,
                                           context=self.context,
                                           timeout=100,
                                           prompt_recovery=self.prompt_recovery,
                                           dialog=con.connection_provider.get_connection_dialog())
        except Exception as err:
            raise SubCommandFailure("Failed to initialise the standby",
                                    err)

        if not sync_standby:
            con.log.info("Standby state check disabled on user request")
        else:
            counter = 0
            while counter < switchover_counter:
                con.active.spawn.sendline("\r")
                con.active.spawn.expect(".*")
                try:
                    rp_state = con.get_rp_state(target='standby',
                                                timeout=60)
                except (SubCommandFailure, TimeoutError):
                    sleep(9)
                    counter += 1
                    continue
                except Exception:
                    con.active.spawn.sendline("\r")
                    con.active.spawn.expect(".*")
                    continue
                else:
                    if re.search('STANDBY HOT', rp_state):
                        counter = switchover_counter + 1
                    else:
                        sleep(9)
                        counter += 1

            # Issue init commands to disable console logging
            exec_commands = self.connection.settings.HA_INIT_EXEC_COMMANDS
            for command in exec_commands:
                con.execute(command)
            config_commands = self.connection.settings.HA_INIT_CONFIG_COMMANDS
            config_retry = 0
            while config_retry < 20:
                try:
                    con.configure(config_commands, timeout=60)
                except Exception as err:
                    if re.search("Config mode cannot be entered",
                                 str(err)):
                        sleep(9)
                        con.active.spawn.sendline()
                        config_retry += 1
                else:
                    config_retry = 21

            # Clear Standby buffer
            con.standby.spawn.sendline("\r")
            con.standby.spawn.expect(".*")
            con.disconnect()
            con.connect()
            # Verify switchover is Successful
        if con.active.start == standby_start_cmd:
            con.log.info("Switchover is Successful")
            self.result = True
        else:
            con.log.info("Switchover is Failed")
            self.result = False


class ResetStandbyRP(BaseService):
    """ Service to reset the standby rp.


        :arg : command : command to be issued on device to reset the standby.
               default command is "system standby manual-boot"

               dialog : Dialog which include list of Statements for
                        additional dialogs prompted by standby reset command,
                        in-case it is not in the current list.

               timeout : Timeout value in sec, Default Value is 500 sec

        :return : True on Success
                  raise SubCommandFailure on failure.

        Example ::

                  rtr.reset_standby_rp()

                  # If command is other than 'system standby manual-boot'
                  rtr.reset_standby_rp(command="command which invoke reload on standby-rp",
                             timeout=600)

    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.result = None
        self.service_name = 'reset_standby_rp'
        self.timeout = connection.settings.HA_RELOAD_TIMEOUT
        self.dialog = Dialog(standby_reset_rp_statement_list)
        self.command = 'system standby manual-boot'
        self.__dict__.update(kwargs)

    def call_service(self, command='system standby manual-boot',
                     reply=Dialog([]),
                     timeout=None,
                     *args,
                     **kwargs):
        # create an alias for connection.
        con = self.connection
        con.log.warning("reset_standby_rp is not supported on NXOS")
        return
        command = command or self.command
        timeout = timeout or self.timeout
        # resetting the standby rp for
        con.log.debug("+++ Issuing reset on  %s  with "
                      "reset_command %s and timeout is %s +++"
                      % (con.hostname, command, timeout))

        # Check is switchover possible?
        rp_state = con.get_rp_state(target='standby', timeout=100)
        if rp_state.find('DISABLED') == "-1":
            raise SubCommandFailure("No Standby found")

        dialog = self.service_dialog(handle=con.active,
                                     service_dialog=self.dialog)
        # Issue switchover command
        con.active.spawn.sendline(command)
        try:
            dialog.process(con.active.spawn, context=self.context, timeout=30)
        except TimeoutError:
            pass
        except SubCommandFailure as err:
            raise SubCommandFailure("Failed to reset standby rp %s" % str(err))

        reset_counter = timeout / 10

        counter = 0
        while counter < reset_counter:
            try:
                rp_state = con.get_rp_state(target='standby',
                                            timeout=60)
            except (SubCommandFailure, TimeoutError):
                sleep(10)
                counter += 1
                continue
            else:
                if re.search('STANDBY HOT', rp_state):
                    counter = reset_counter + 1
                else:
                    sleep(10)
                    counter += 1

        # Clear Standby buffer
        try:
            con.standby.spawn.sendline("\r")
            con.standby.spawn.expect(".*")
            con.standby.state_machine.go_to('any',
                                            con.standby.spawn,
                                            context=self.context,
                                            timeout=100,
                                            dialog=con.connection_provider.get_connection_dialog())
            con.enable(target='standby')
        except SubCommandFailure as err:
            raise SubCommandFailure(
                "Failed to bring the standby to enable state : %s" % str(err))
        con.log.info("Successfully reloaded Standby RP")
        self.result = True


class ShellExec(BaseService):
    """ Service to execute commands on shell.

    Arguments:
        command: List of command to execute on shell
        dialog: Dialog which include list of Statements for
                additional dialogs prompted by command executed,
                in-case it is not in the current list.
        timeout: Timeout value in sec for executing command on shell.

    Returns:
        string: console output on success

    Raises:
        SubCommandFailure: on failure.

    Example:
        .. code-block:: python

            rtr.shellexec(['uname -a'])
            cmd = ['uname -a', 'ls -l']
            dev.shellexec(cmd)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'shell'
        self.end_state = 'enable'
        self.service_name = 'shellexec'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.result = None
        self.__dict__.update(kwargs)

    def call_service(self, command=[],
                     reply=Dialog([]),
                     timeout=None,
                     *args, **kwargs):
        con = self.connection
        timeout = timeout or self.timeout
        self.command_list_is_empty = False
        try:
            con.state_machine.go_to(self.start_state,
                                    con.spawn,
                                    context=self.context)
        except Exception as err:
            raise SubCommandFailure("Failed to Bring device to shell State",
                                    err)
        # if commands is a list
        if isinstance(command, collections.Sequence):
            # No command passed, just move to config mode
            if len(command) == 0:
                self.result = " "
                self.command_list_is_empty = True
            elif len(command) == 1:
                dialog = self.service_dialog(service_dialog=reply)
                con.spawn.sendline(command[0])
                try:
                    self.result = dialog.process(con.spawn, timeout=timeout)
                except Exception as err:
                    raise SubCommandFailure(
                        "Failed to execute command on shell", err)
                self.result = self.result.match_output
                if self.result.rfind(self.connection.hostname):
                    self.result = self.result[
                                  :self.result.rfind(self.connection.hostname)]
            else:
                dialog = self.service_dialog(service_dialog=reply)
                # Commands are list of more than one command
                for cmd in command:
                    con.spawn.sendline(cmd)
                    try:
                        self.result = dialog.process(con.spawn,
                                                     context=self.context,
                                                     timeout=timeout)
                    except Exception as err:
                        raise SubCommandFailure(
                            "Failed to execute command on shell", err)
                con.state_machine.go_to(self.end_state, con.spawn,
                                        context=self.context)
                self.result = self.result.match_output
                if self.result.rfind(self.connection.hostname):
                    self.result = self.result[
                                  :self.result.rfind(self.connection.hostname)]
        else:
            dialog = self.service_dialog(service_dialog=reply)
            con.spawn.sendline(command)
            try:
                self.result = dialog.process(con.spawn,
                                             context=self.context,
                                             timeout=timeout)
            except Exception as err:
                raise SubCommandFailure("Failed to execute command on shell",
                                        err)
            con.state_machine.go_to(self.end_state, con.spawn,
                                    context=self.context)
            self.result = self.result.match_output
            if self.result.rfind(self.connection.hostname):
                self.result = self.result[
                              :self.result.rfind(self.connection.hostname)]

    def post_service(self, *args, **kwargs):
        if self.command_list_is_empty:
            pass
        else:
            state_machine = self.connection.state_machine
            state_machine.go_to(self.end_state,
                                self.connection.spawn,
                                context=self.connection.context)


class HAShellExec(BaseService):
    """ Service to execute commands on shell.

    Arguments:
        command: List of command to execute on shell
        dialog: Dialog which include list of Statements for
                additional dialogs prompted by command executed,
                in-case it is not in the current list.
        timeout : Timeout value in sec for executing command on shell.

    Returns:
        console output:  on Success

    Raises:
        SubCommandFailure: on failure.

    Example ::
        .. code-block:: python

            rtr.shellexec(['uname -a'])
            cmd = ['uname -a', 'ls -l']
            dev.shellexec(cmd)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'shell'
        self.end_state = 'enable'
        self.service_name = 'shellexec'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.result = None
        # add the keyword arguments to the object
        self.__dict__.update(kwargs)

    def call_service(self, command=[],
                     reply=Dialog([]),
                     timeout=None,
                     target=None,
                     *args, **kwargs):
        con = self.connection
        con.log.debug("+++ shellexec  +++")
        timeout = timeout or self.timeout
        self.command_list_is_empty = False

        if target == 'standby':
            spawn = con.standby.spawn
            handle = con.standby
            state_machine = con.standby.state_machine
            try:
                state_machine.go_to(self.start_state,
                                    spawn,
                                    context=self.context)
            except Exception as err:
                raise SubCommandFailure("Failed to Bring device to Shell State",
                                        err)
        else:
            spawn = con.active.spawn
            handle = con.active
            state_machine = con.active.state_machine
            try:
                state_machine.go_to(self.start_state,
                                    spawn,
                                    context=self.context)
            except Exception as err:
                raise SubCommandFailure("Failed to Bring device to shell State",
                                        err)

        # if commands is a list
        if isinstance(command, collections.Sequence):
            # No command passed, just move to config mode
            if len(command) == 0:
                self.result = " "
                self.command_list_is_empty = True
            elif len(command) == 1:
                dialog = self.service_dialog(service_dialog=reply,
                                             handle=handle)
                spawn.sendline(command[0])
                try:
                    self.result = dialog.process(spawn, timeout=timeout)
                except Exception as err:
                    raise SubCommandFailure(
                        "Failed to Bring device to shell State", err)
                self.result = self.result.match_output
                if self.result.rfind(self.connection.hostname):
                    self.result = self.result[
                                  :self.result.rfind(self.connection.hostname)]
            else:
                dialog = self.service_dialog(service_dialog=reply,
                                             handle=handle)
                # Commands are list of more than one command
                for cmd in command:
                    spawn.sendline(cmd)
                    try:
                        self.result = dialog.process(spawn, timeout=timeout)
                    except Exception as err:
                        raise SubCommandFailure("Configuration failed", err)
                state_machine.go_to(self.end_state, spawn, context=self.context)
                self.result = self.result.match_output
                if self.result.rfind(self.connection.hostname):
                    self.result = self.result[
                                  :self.result.rfind(self.connection.hostname)]
        else:
            dialog = self.service_dialog(service_dialog=reply, handle=handle)
            spawn.sendline(command)
            try:
                self.result = dialog.process(spawn,
                                             context=self.context,
                                             timeout=timeout)
            except Exception as err:
                raise SubCommandFailure("Configuration failed", err)
            state_machine.go_to(self.end_state, spawn, context=self.context)
            self.result = self.result.match_output
            if self.result.rfind(self.connection.hostname):
                self.result = self.result[
                              :self.result.rfind(self.connection.hostname)]

    def post_service(self, *args, **kwargs):
        if self.command_list_is_empty:
            pass
        else:
            state_machine = self.connection.active.state_machine
            state_machine.go_to(self.end_state,
                                self.connection.active.spawn,
                                context=self.connection.context)


class ListVdc(BaseService):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        service_name = 'list_vdc'

    def call_service(self, timeout=10, command="show vdc"):
        initial_vdc = self.connection.current_vdc
        # in case not on default vdc then switchback
        if initial_vdc:
            self.connection.switchback()
        buffer = self.connection.execute("show vdc", timeout=timeout)
        self.result = re.findall(r'^\d+\s+(\S+)', buffer, re.MULTILINE)
        if initial_vdc:
            self.connection.switchto(initial_vdc)


class SwitchVdc(BaseService):
    """Switch to a given VDC Name

    This command is available on the 'switchto' attribute of the connection
    object. In case the user is already on a VDC, it can switchback to the
    default and again switch to the said vdc, hence this command can be issued
    even from other VDCs

    Arguments:
        vdc_name: name of the vdc to switch to.
        timeout: timeout for the whole operations.
        dialog: additional dialog provided by the user.
        vdc_passwd: required for first login, defaults to tacacs password.
        command: alternate command to be used.

    Example:
        .. code-block:: python

            con.switchto("vdc2")

    Raises:
        SubCommandFailure Error
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.service_name = 'switchto vdc'

    def call_service(self, vdc_name,
                     timeout=20,
                     command="switchto vdc",
                     dialog=Dialog([]),
                     vdc_passwd=None):
        vdc_passwd = vdc_passwd or self.connection.context.tacacs_password
        command = command + " " + vdc_name

        # if we are already on the same vdc, just bypass the call
        if self.connection.current_vdc == vdc_name:
            self.connection.log.info("device already on %s" % vdc_name)
            return vdc_name

        # vdc name must be valid one.
        vdc_list = self.connection.list_vdc()
        if vdc_name not in vdc_list:
            raise SubCommandFailure("invalid vdc name: %s" % vdc_name)

        # in case we are on a VDC already, we need to switchback first
        if self.connection.current_vdc is not None and \
                        self.connection.current_vdc != vdc_name:
            self.connection.switchback()

        new_hostname = self.connection.hostname + '-' + vdc_name
        if self.connection.is_ha:
            self.connection.active.state_machine.hostname = new_hostname
            self.connection.standby.state_machine.hostname = new_hostname
        else:
            self.connection.state_machine.hostname = new_hostname

        # prepare the dialog to be used.
        command_dialog = Dialog([
            [patterns.secure_password, send_response, {'response': "yes"}, True,
             True],
            [patterns.admin_password, send_response, {'response': vdc_passwd},
             True, True],
            [patterns.setup_dialog, send_response, {'response': "no"}, True,
             True],
        ])
        # append the dialog which user has provided.
        command_dialog += dialog

        try:
            self.connection.execute(command, reply=command_dialog,
                                    timeout=timeout)
        except Exception as err:
            # this means there was some problem during the switching. Hence
            # rollback all the changes to the state machine
            if self.connection.is_ha:
                self.connection.active.state_machine.hostname = \
                    self.connection.hostname
                self.connection.standby.state_machine.hostname = \
                    self.connection.hostname
            else:
                # update the vdc name in connection
                self.connection.state_machine.hostname = \
                    self.connection.hostname
                SubCommandFailure("failed to switch to vdc %s" % vdc_name)
        else:
            self.connection.current_vdc = vdc_name
            # init the connection after switching into a vdc
            if self.connection.is_ha:
                self.connection.connection_provider.init_active()
            else:
                # duck type this properly in connection class.
                self.connection.connection_provider.init_handle()
            self.result = vdc_name


class SwitchbackVdc(BaseService):
    """switches back to default vdc"""

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.service_name = 'switchback'

    def call_service(self, timeout=10, command="switchback", dialog=Dialog()):
        # this service should be called only if we are on the VDC
        if self.connection.current_vdc:
            hostname = self.connection.hostname
            if self.connection.is_ha:
                self.connection.active.state_machine.hostname = hostname
                self.connection.standby.state_machine.hostname = hostname
            else:
                self.connection.state_machine.hostname = hostname
            self.connection.execute(command, timeout=timeout, reply=dialog)
            self.connection.current_vdc = None
        else:
            self.connection.log.info("already on default vdc")


class CreateVdc(BaseService):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.service_name = "create vdc"

    def call_service(self, vdc_name, command="vdc", dialog=Dialog(),
                     timeout=120):
        initial_vdc = self.connection.current_vdc
        # Stringify command in case it is passed in as an object.
        command = str(command) + " " + vdc_name
        # the vdc should not be already present
        vdc_list = self.connection.list_vdc()
        if vdc_name in vdc_list:
            raise SubCommandFailure("vdc %s already exists" % vdc_name)

        # if not on default vdc then switchback before creating vdc
        if initial_vdc:
            self.connection.switchback()

        self.connection.configure(command, timeout=timeout, reply=dialog)
        self.result = vdc_name

        # if user was on some vdc when issuing this subcommand then switch
        # him back
        if initial_vdc:
            self.connection.switchto(initial_vdc)


class DeleteVdc(BaseService):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = "enable"
        self.end_state = "enable"
        self.service_name = "delete vdc"

    def call_service(self, vdc_name, command="no vdc", dialog=Dialog(),
                     timeout=90):
        # Stringify the command in case it is passed as an object.
        command = str(command) + " " + vdc_name
        initial_vdc = self.connection.current_vdc

        # cant delete the vdc on which device is present right now.
        if vdc_name == initial_vdc:
            raise SubCommandFailure(
                "can't delete vdc %s because device is already on that vdc"
                % vdc_name)

        # device must be in default vdc
        if initial_vdc:
            self.connection.switchback()

        # vdc must exist before it can be deleted.
        vdc_list = self.connection.list_vdc()
        if vdc_name not in vdc_list:
            raise SubCommandFailure("vdc %s doesn't exist" % vdc_name)

        # form the dialog
        command_dialog = Dialog([
            [patterns.delete_vdc_confirm, send_response, {'response': "yes"},
             True, True]
        ])

        # add user dialog if provided
        command_dialog += dialog
        self.connection.configure(
            command, reply=command_dialog, timeout=timeout)
        self.result = vdc_name

        # if the device was no some vdc while issue this command then change
        # vdc to initial_vdc
        if initial_vdc:
            self.connection.switchto(initial_vdc)
