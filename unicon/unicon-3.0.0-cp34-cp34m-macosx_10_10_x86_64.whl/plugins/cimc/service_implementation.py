__copyright__ = "# Copyright (c) 2017 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.bases.routers.services import BaseService
from unicon.eal.dialogs import Dialog, Statement

from unicon.plugins.generic.statements import GenericStatements

from unicon.plugins.cimc.patterns import CimcPatterns

from unicon.plugins.generic import GenericUtils

utils = GenericUtils()


class Execute(BaseService):
    """ Execute Service implementation

    Service  to executes exec_commands on the device and return the
    console output. reply option can be passed for the interactive exec
    command.

    Arguments:
        command: exec command
        reply: Additional Dialog patterns for interactive exec commands.
        timeout : Timeout value in sec, Default Value is 60 sec

    Returns:
        True on Success, raise SubCommandFailure on failure

    Example:
        .. code-block:: python

              output = dev.execute("show command")

    """

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'shell'
        self.end_state = 'shell'
        self.service_name = 'execute'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.__dict__.update(kwargs)

    def call_service(self, command,
                     reply=Dialog([]),
                     timeout=None,
                     *args, **kwargs):

        con = self.connection
        timeout = timeout or self.timeout
        if not isinstance(reply, Dialog):
            raise SubCommandFailure(
                "dialog passed via 'reply' must be an instance of Dialog")
        dialog = self.service_dialog(service_dialog=reply)

        con.sendline(command)
        try:
            self.result = dialog.process(con.spawn,
                                         timeout=timeout,
                                         context=self.context)
        except Exception as err:
            raise SubCommandFailure("Command execution failed", err)

        # Remove command and hostname from output.
        self.result = self.result.match_output.replace(command, "").lstrip()
        # Get output of command after removing the state pattern.
        self.result = utils.truncate_trailing_prompt(
            con.state_machine.get_state(con.state_machine.current_state),
            self.result, self.connection.hostname)
