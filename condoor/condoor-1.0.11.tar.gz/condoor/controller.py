"""Provides the Controller class which is a wrapper to the pyexpect.spawn class."""

import re
import pexpect
from time import time

from condoor.utils import delegate, levenshtein_distance
from condoor.exceptions import ConnectionError, ConnectionTimeoutError


# Delegate following methods to _session class
@delegate("_session", ("expect", "expect_exact", "expect_list", "compile_pattern_list", "sendline",
                       "isalive", "sendcontrol", "send", "read_nonblocking", "setecho", "delaybeforesend",
                       "waitnoecho"))
class Controller(object):
    """Controller class which wraps the pyexpect.spawn class."""

    def __init__(self, connection):
        """Initialize the Controller object for specific connection."""
        # delegated pexpect session
        self._session = None
        self._connection = connection

        self._logfile_fd = connection.session_fd
        self.connected = False
        self.authenticated = False
        self.last_hop = 0

    @property
    def hostname(self):
        """Return the hostname."""
        return self._connection.hostname

    def spawn_session(self, command):
        """Spawn the session using proper command."""
        if self._session and self.isalive():  # pylint: disable=no-member
            self._connection.log("Executing command: '{}'".format(command))
            try:
                self.send(command)  # pylint: disable=no-member
                self.expect_exact(command, timeout=20)  # pylint: disable=no-member
                self.sendline()  # pylint: disable=no-member

            except (pexpect.EOF, OSError):
                raise ConnectionError("Connection error", self.hostname)
            except pexpect.TIMEOUT:
                raise ConnectionTimeoutError("Timeout", self.hostname)

        else:
            self._connection.log("Spawning command: '{}'".format(command))
            try:
                self._session = pexpect.spawn(
                    command,
                    maxread=65536,
                    searchwindowsize=4000,
                    env={"TERM": "vt100"},  # to avoid color control characters
                    echo=True  # KEEP YOUR DIRTY HANDS OFF FROM ECHO!
                )
                self._session.delaybeforesend = 0.3
                self._connection.log("Child process FD: {}".format(self._session.child_fd))
                rows, cols = self._session.getwinsize()
                if cols < 180:
                    self._session.setwinsize(512, 240)
                    nrows, ncols = self._session.getwinsize()
                    self._connection.log("Terminal window size changed from {}x{} to {}x{}".format(
                        rows, cols, nrows, ncols))
                else:
                    self._connection.log("Terminal window size: {}x{}".format(rows, cols))

            except pexpect.EOF:
                raise ConnectionError("Connection error", self.hostname)
            except pexpect.TIMEOUT:
                raise ConnectionTimeoutError("Timeout", self.hostname)

            self.set_session_log(self._logfile_fd)
            self.connected = True

    def set_session_log(self, session_log_fd=None):
        """Set the fd for session log."""
        self._connection.log("Setting the session log")
        if self._session:
            self._session.logfile_read = session_log_fd

    def send_command(self, cmd, password=False):
        """Send command."""
        try:
            if password:
                timeout = 10
                self._connection.log("Waiting for ECHO OFF")
                if self.waitnoecho(timeout):  # pylint: disable=no-member
                    self._connection.log("Password ECHO OFF received")
                else:
                    self._connection.log("Password ECHO OFF not received within {}s".format(timeout))
                self.sendline(cmd)  # pylint: disable=no-member
            else:
                self.send(cmd)  # pylint: disable=no-member
                self.expect_exact([cmd, pexpect.TIMEOUT], timeout=15)  # pylint: disable=no-member
                self.sendline()  # pylint: disable=no-member
        except OSError:
            self._connection.log("Session already disconnected.")
            raise ConnectionError("Session already disconnected")

    def disconnect(self):
        """Disconnect the controller."""
        if self._session and self._session.isalive():
            self._connection.log("Disconnecting the sessions")
            self._session.close(force=True)
            self._session.wait()
        self._connection.log("Disconnected")
        self.connected = False

    def try_read_prompt(self, timeout_multiplier):
        """Read the prompt.

        Based on try_read_prompt from pxssh.py
        https://github.com/pexpect/pexpect/blob/master/pexpect/pxssh.py
        """
        # maximum time allowed to read the first response
        first_char_timeout = timeout_multiplier * 2

        # maximum time allowed between subsequent characters
        inter_char_timeout = timeout_multiplier * 0.4

        # maximum time for reading the entire prompt
        total_timeout = timeout_multiplier * 4

        prompt = ""
        begin = time()
        expired = 0.0
        timeout = first_char_timeout

        while expired < total_timeout:
            try:
                char = self.read_nonblocking(size=1, timeout=timeout)  # pylint: disable=no-member
                # \r=0x0d CR \n=0x0a LF
                if char not in ['\n', '\r']:  # omit the cr/lf sent to get the prompt
                    timeout = inter_char_timeout
                expired = time() - begin
                prompt += char
            except pexpect.TIMEOUT:
                break
            except pexpect.EOF:
                raise ConnectionError('Session disconnected')

        prompt = prompt.strip()
        return prompt

    def detect_prompt(self, sync_multiplier=4):
        """Detect the prompt.

        This attempts to find the prompt. Basically, press enter and record
        the response; press enter again and record the response; if the two
        responses are similar then assume we are at the original prompt.
        This can be a slow function. Worst case with the default sync_multiplier
        can take 16 seconds. Low latency connections are more likely to fail
        with a low sync_multiplier. Best case sync time gets worse with a
        high sync multiplier (500 ms with default).

        """
        self.sendline()  # pylint: disable=no-member
        self.try_read_prompt(sync_multiplier)

        attempt = 0
        max_attempts = 10
        while attempt < max_attempts:
            attempt += 1
            self._connection.log("Detecting prompt. Attempt ({}/{})".format(attempt, max_attempts))

            self.sendline()  # pylint: disable=no-member
            first = self.try_read_prompt(sync_multiplier)

            self.sendline()  # pylint: disable=no-member
            second = self.try_read_prompt(sync_multiplier)

            lhd = levenshtein_distance(first, second)
            len_first = len(first)
            self._connection.log("LD={},MP={}".format(lhd, sync_multiplier))
            sync_multiplier *= 1.2
            if len_first == 0:
                continue

            if float(lhd) / len_first < 0.3:
                prompt = second.splitlines(True)[-1]
                self._connection.log("Detected prompt: '{}'".format(prompt))
                compiled_prompt = re.compile("(\r\n|\n\r){}".format(re.escape(prompt)))
                self.sendline()  # pylint: disable=no-member
                self.expect(compiled_prompt)  # pylint: disable=no-member
                return prompt

        return None

    @property
    def is_connected(self):
        """Return the session state regardless of device connection state."""
        return self.connected and self._session and self._session.isalive()

    @property
    def before(self):
        """Return text up to the expected string pattern."""
        return self._session.before if self._session else None

    @property
    def after(self):
        """Return text that was matched by the expected pattern."""
        return self._session.after if self._session else None
