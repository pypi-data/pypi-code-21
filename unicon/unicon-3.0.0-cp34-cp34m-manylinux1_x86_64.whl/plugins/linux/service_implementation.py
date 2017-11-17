import re

from unicon.bases.linux.services import BaseService
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.linux.patterns import LinuxPatterns
from unicon.plugins.linux.utils import LinuxUtils

utils = LinuxUtils()


class Execute(BaseService):
    def __init__(self, connection, context, **kwargs):
        self.connection = connection
        self.context = context
        self.timeout_pattern = ['Timeout occurred', ]
        self.error_pattern = []
        self.start_state = 'None'
        self.end_state = 'None'
        self.result = None
        # add the keyword arguments to the object
        self.__dict__.update(kwargs)

    def call_service(self, command,
                     reply=Dialog([]),
                     timeout=None,
                     *args, **kwargs):

        con = self.connection
        con.log.debug("+++ execute %s +++" % command)
        timeout = timeout or con.settings.EXEC_TIMEOUT
        if not isinstance(reply, Dialog):
            raise SubCommandFailure(
                "dialog passed via 'reply' must be an instance of Dialog")
        p = LinuxPatterns()
        dialog = Dialog()
        if reply:
            dialog += reply
        dialog.append(Statement(pattern=p.prompt))
        con.sendline(command)
        try:
            self.result = dialog.process(con.spawn, timeout=timeout,
                prompt_recovery=self.prompt_recovery)
        except Exception as err:
            raise SubCommandFailure("Command execution failed", err)
        # Remove command and hostname from output.
        if self.result:
            output = utils.truncate_trailing_prompt(
                        con.state_machine.get_state(con.state_machine.current_state).pattern,
                        self.result.match_output,
                        self.connection.hostname)
            output = re.sub(re.escape(command), "", output, 1)
            self.result = output.strip()
