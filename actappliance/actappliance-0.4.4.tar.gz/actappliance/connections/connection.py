import shlex
import logging
from concurrent.futures import ThreadPoolExecutor as Executor
from concurrent.futures import TimeoutError
from actappliance.models import ActResponse
import atexit


class ApplianceConnection(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.timeout = 6 * 60 * 60

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.disconnect()
        atexit.unregister(self.disconnect)

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def prep_cmd(self, operation, **update_cmds):
        """
        Do what needs to be done before sending the command

        :param operation:
        :param update_cmds:
        :return: A ActCmd object from this class
        """
        return self.ActCmd(operation, **update_cmds)

    def call(self, command_obj):
        """Call that gets the unfiltered connections response"""
        raise NotImplementedError

    def _timeout(self, fnc, *args, **kwargs):
        with Executor(max_workers=1) as p:
            f = p.submit(fnc, *args, **kwargs)
            try:
                return f.result(timeout=self.timeout)
            except TimeoutError:
                timeout = "Call timed out after {} seconds.".format(self.timeout)
                self.logger.exception("function: {}\n" +
                                      "args: {}\n" +
                                      "kwargs: {}".format(self.timeout, fnc, args, kwargs))
                raise TimeoutError(timeout)

    def timeout_call(self, command_obj):
        return self._timeout(self.call, command_obj)

    def cmd(self, operation, **update_cmds):
        """Command that makes a call with standardized input and output so it's the same across connections"""
        command = self.prep_cmd(operation, **update_cmds)
        self.timeout_call(command)
        return self.post_cmd(command)

    def post_cmd(self, command_obj):
        """Perform post-cmd handlers and wrap result"""
        # Remove result so we don't save it twice
        result = command_obj.result
        command_obj.result = None
        return ActResponse(result, actifio_command=command_obj)

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
                self.logger.info('No existing filtervalue found returning update_cmd filtervalue only')
                update_cmds['filtervalue'] = filtervalue_append
        return update_cmds

    class ActCmd(object):
        """Class to house attributes for a single cmd"""

        def __init__(self, operation=None, **update_cmds):
            self.operation = operation
            self.update_cmds = update_cmds
            self.call_result = None  # This holds result before it's processed in post_cmd if required
            self.result = None  # This is the temporary holder for the REST-ful response

        def __repr__(self):
            """This will be None if post_cmd gets called, check the ActResponse dictionary for the values"""
            return str(self.result)
