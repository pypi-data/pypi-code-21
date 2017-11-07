import os
import subprocess
import logging

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.instrumentation import safe_wrap_function
from tcell_agent.instrumentation.manager import InstrumentationManager
from tcell_agent.utils.compat import a_string


LOGGER = logging.getLogger('tcell_agent').getChild(__name__)

DJANGO_ACTIVE = False
FLASK_ACTIVE = False


try:
    import django  # noqa pylint: disable=relative-import,unused-import
    DJANGO_ACTIVE = True

except ImportError:
    pass

try:
    from flask import Flask  # noqa pylint: disable=relative-import,unused-import
    FLASK_ACTIVE = True
except ImportError:
    pass


# easy patching in tests
def django_active():
    return DJANGO_ACTIVE


# easy patching in tests
def flask_active():
    return FLASK_ACTIVE


def get_tcell_context():
    if django_active():
        from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware
        request = GlobalRequestMiddleware.get_current_request()
        if request and request._tcell_context:
            return request._tcell_context

    elif flask_active():
        from flask.globals import _request_ctx_stack
        if _request_ctx_stack.top and _request_ctx_stack.top.request:
            return _request_ctx_stack.top.request._tcell_context

    return None


def should_block_shell_command(cmd):
    def wrapped_should_block_shell_command(command):
        if command is None:
            return False

        if not a_string(command):
            command = ' '.join(command)

        tcell_context = get_tcell_context()
        command_injection_policy = TCellAgent.get_policy(PolicyTypes.COMMAND_INJECTION)
        return command_injection_policy.block(command, tcell_context)

    return safe_wrap_function("Checking cmdi", wrapped_should_block_shell_command, cmd) or False


def instrument_os_system():
    class TCellDefaultFlag(object):
        pass

    def _tcell_os_system(_tcell_original_system, cmd):
        if should_block_shell_command(cmd):
            return 1
        else:
            return _tcell_original_system(cmd)
    InstrumentationManager.instrument(os, "system", _tcell_os_system)

    def _tcell_os_popen(_tcell_original_popen, command, mode='r', bufsize=TCellDefaultFlag):
        if should_block_shell_command(command):
            from tempfile import TemporaryFile
            result = TemporaryFile(mode)
            return result
        else:
            if bufsize is TCellDefaultFlag:
                return _tcell_original_popen(command, mode)
            else:
                return _tcell_original_popen(command, mode, bufsize)
    InstrumentationManager.instrument(os, "popen", _tcell_os_popen)

    def _tcell_os_popen_two(_tcell_original_popen_two, cmd, mode='t', bufsize=TCellDefaultFlag):
        if should_block_shell_command(cmd):
            from tempfile import TemporaryFile
            writeable = TemporaryFile('w')
            output = TemporaryFile('r')
            return (writeable, output)

        else:
            if bufsize is TCellDefaultFlag:
                return _tcell_original_popen_two(cmd, mode)
            else:
                return _tcell_original_popen_two(cmd, mode, bufsize)

    if hasattr(os, "popen2"):
        InstrumentationManager.instrument(os, "popen2", _tcell_os_popen_two)

    def _tcell_os_popen_three(_tcell_original_popen_three, cmd, mode='t', bufsize=TCellDefaultFlag):
        if should_block_shell_command(cmd):
            from tempfile import TemporaryFile
            writeable = TemporaryFile('w')
            readable = TemporaryFile('r')
            error = TemporaryFile('r')
            return (writeable, readable, error)
        else:
            if bufsize is TCellDefaultFlag:
                return _tcell_original_popen_three(cmd, mode)
            else:
                return _tcell_original_popen_three(cmd, mode, bufsize)
    if hasattr(os, "popen3"):
        InstrumentationManager.instrument(os, "popen3", _tcell_os_popen_three)

    def _tcell_os_popen_four(_tcell_original_popen_four, cmd, mode='t', bufsize=TCellDefaultFlag):
        if should_block_shell_command(cmd):
            from tempfile import TemporaryFile
            writeable = TemporaryFile('w')
            output_n_error = TemporaryFile('r')
            return (writeable, output_n_error)
        else:
            if bufsize is TCellDefaultFlag:
                return _tcell_original_popen_four(cmd, mode)
            else:
                return _tcell_original_popen_four(cmd, mode, bufsize)
    if hasattr(os, "popen4"):
        InstrumentationManager.instrument(os, "popen4", _tcell_os_popen_four)

    def _tcell_subprocess_call(
            _tcell_original_subprocess_call,
            args,
            bufsize=0,
            executable=None,
            stdin=None,
            stdout=None,
            stderr=None,
            preexec_fn=None,
            close_fds=False,
            shell=False,
            cwd=None,
            env=None,
            universal_newlines=False,
            startupinfo=None,
            creationflags=0):
        if should_block_shell_command(args):
            return 1
        else:
            return _tcell_original_subprocess_call(
                args,
                bufsize=bufsize,
                executable=executable,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                preexec_fn=preexec_fn,
                close_fds=close_fds,
                shell=shell,
                cwd=cwd,
                env=env,
                universal_newlines=universal_newlines,
                startupinfo=startupinfo,
                creationflags=creationflags)
    InstrumentationManager.instrument(subprocess, "call", _tcell_subprocess_call)

    def _tcell_subprocess_check_output(
            _tcell_original_subprocess_check_output,
            args,
            bufsize=0,
            executable=None,
            stdin=None,
            stderr=None,
            preexec_fn=None,
            close_fds=False,
            shell=False,
            cwd=None,
            env=None,
            universal_newlines=False,
            startupinfo=None,
            creationflags=0):
        if should_block_shell_command(args):
            raise subprocess.CalledProcessError(1, args, b"Blocked by TCell")
        else:
            return _tcell_original_subprocess_check_output(
                args,
                bufsize=bufsize,
                executable=executable,
                stdin=stdin,
                stderr=stderr,
                preexec_fn=preexec_fn,
                close_fds=close_fds,
                shell=shell,
                cwd=cwd,
                env=env,
                universal_newlines=universal_newlines,
                startupinfo=startupinfo,
                creationflags=creationflags)
    InstrumentationManager.instrument(subprocess, "check_output", _tcell_subprocess_check_output)

    try:
        import popen2

        def _tcell_popen2_popen_two(_tcell_original_popen_two, cmd, bufsize=TCellDefaultFlag, mode='t'):
            if should_block_shell_command(cmd):
                from tempfile import TemporaryFile
                writeable = TemporaryFile('w')
                output = TemporaryFile('r')
                return (writeable, output)

            else:
                if bufsize is TCellDefaultFlag:
                    return _tcell_original_popen_two(cmd, mode=mode)
                else:
                    return _tcell_original_popen_two(cmd, bufsize, mode)
        InstrumentationManager.instrument(popen2, "popen2", _tcell_popen2_popen_two)

        def _tcell_popen2_popen_three(_tcell_original_popen_three, cmd, bufsize=TCellDefaultFlag, mode='t'):
            if should_block_shell_command(cmd):
                from tempfile import TemporaryFile
                writeable = TemporaryFile('w')
                readable = TemporaryFile('r')
                error = TemporaryFile('r')
                return (writeable, readable, error)
            else:
                if bufsize is TCellDefaultFlag:
                    return _tcell_original_popen_three(cmd, mode=mode)
                else:
                    return _tcell_original_popen_three(cmd, bufsize, mode)
        InstrumentationManager.instrument(popen2, "popen3", _tcell_popen2_popen_three)

        def _tcell_popen2_popen_four(_tcell_original_popen_four, cmd, bufsize=TCellDefaultFlag, mode='t'):
            if should_block_shell_command(cmd):
                from tempfile import TemporaryFile
                writeable = TemporaryFile('w')
                output_n_error = TemporaryFile('r')
                return (writeable, output_n_error)
            else:
                if bufsize is TCellDefaultFlag:
                    return _tcell_original_popen_four(cmd, mode=mode)
                else:
                    return _tcell_original_popen_four(cmd, bufsize, mode)
        InstrumentationManager.instrument(popen2, "popen4", _tcell_popen2_popen_four)

    except ImportError:
        pass


try:
    instrument_os_system()
except Exception as e:
    LOGGER.debug("Could not instrument for cmdi: {e}".format(e=e))
    LOGGER.debug(e, exc_info=True)
