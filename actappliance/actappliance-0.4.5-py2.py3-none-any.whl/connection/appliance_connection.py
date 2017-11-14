import shlex
import logging
import signal

from actappliance.models import ActResponse


def call_timeout_handler(signum, frame):
    logging.info("Call appears to be hanging, killing call.")
    raise RuntimeError("Call took longer than the timeout. Killing call.")


class ApplianceConnection(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        signal.signal(signal.SIGALRM, call_timeout_handler)

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def pre_cmd_handler(self, operation, **update_cmds):
        """
        Do what needs to be done before sending the command

        :param operation:
        :param update_cmds:
        :return: A ActCmd object from this class
        """
        prepared_command = self.Command(operation, **update_cmds)
        return prepared_command

    def call(self, command_obj):
        """
        Call that gets the unfiltered connections response

        :param timeout: time in seconds to wait for the call. default: 6 hours
        """
        raise NotImplementedError

    def post_cmd_handler(self, command_obj):
        """Perform post-cmd handlers and wrap result"""
        # Remove result so we don't save it twice
        result = command_obj.result
        command_obj.result = None
        return ActResponse(result, actifio_command=command_obj)

    def cmd(self, operation, **update_cmds):
        """ActCmd that makes a call with standardized input and output so it's the same across connections"""
        command = self.pre_cmd_handler(operation, **update_cmds)
        self.call(command)
        return self.post_cmd_handler(command)

    def append_filtervalue(self, command, **update_cmds):
        """
        Takes a operation and an update_cmds dict and adds the new filtervalues to the existing one instead of
        overwriting.

        :param command:
        :param update_cmds:
        :return: operation and correctly appended update_cmds
        """
        # handle no input
        if 'filtervalue' not in update_cmds:
            # return empty string so that update will function without TypeError
            return ''
        filtervalue_append = update_cmds.pop('filtervalue')
        if filtervalue_append:
            s_command = shlex.split(command)
            for word in enumerate(s_command):
                if word[1] == '-filtervalue':
                    position = word[0]
                    update_cmds['filtervalue'] = "{}&{}".format(s_command[position + 1], filtervalue_append)
            try:
                update_cmds['filtervalue']
            except KeyError:
                self.logger.warning('No existing filtervalue found returning update_cmd filtervalue only')
                update_cmds['filtervalue'] = filtervalue_append
        return update_cmds

    class Command(object):
        """Class to house attributes for a single cmd"""

        def __init__(self, operation=None, **update_cmds):
            self.operation = operation
            self.update_cmds = update_cmds
            self.result = None  # This is the temporary holder for the REST-ful response

        def __repr__(self):
            """This will be None if post_cmd gets called, check the ActResponse dictionary for the values"""
            return str(self.result)
