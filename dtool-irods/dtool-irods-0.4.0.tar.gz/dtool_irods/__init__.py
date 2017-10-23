"""dtool_irods package."""

import sys
import logging
from subprocess import Popen, PIPE

__version__ = "0.4.0"

logger = logging.getLogger(__name__)


class CommandWrapper(object):
    """Class for creating API calls from command line tools."""

    def __init__(self, args):
        self.args = args

    def success(self):
        """Return True if the command line tool was run successfully."""
        return self.returncode == 0

# Useful helper functions

    def _call_cmd_line(self):
        """Run the command line tool."""
        try:
            logging.info("Calling Popen with: {}".format(self.args))
            p = Popen(self.args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        except OSError:
            raise(RuntimeError("No such command found in PATH"))

        # Calling this command with newline as stdin as the
        # iCommnads hangs waiting for user input if the password
        # has not been set or has timed out.
        self.stdout, self.stderr = p.communicate("\n")
        self.stdout = self.stdout.decode("utf-8")
        self.stderr = self.stderr.decode("utf-8")
        self.returncode = p.returncode

# Interface API.

    def __call__(self, exit_on_failure=True):
        """Return wrapped stdout or raise if stderr is not empty."""
        self._call_cmd_line()

        if self.success():
            return self.stdout
        else:
            if exit_on_failure:
                logger.warning("Command failed: {}".format(self.args))
                logger.warning(self.stderr)
                sys.stderr.write(self.stderr)

                # The iRODS setup has probably not been configured at all.
                if self.stderr.find("USER_RODS_HOST_EMPTY") != -1:
                    print("Try running the iRODS command: iinit")

                # The iRODS authentication has probably timed out.
                if self.stderr.find("CAT_INVALID_AUTHENTICATION") != -1:
                    print("Try running the iRODS command: iinit")

                sys.exit(self.returncode)
            else:
                logger.info("Command failed: {}".format(self.args))
                logger.info(self.stderr)
