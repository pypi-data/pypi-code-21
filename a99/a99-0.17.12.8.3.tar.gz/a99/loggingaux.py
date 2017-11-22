"""Logging routines"""


__all__ = [
"get_python_logger", "add_file_handler",
"LogTwo", "SmartFormatter", "str_exc"]


import logging
import sys
from argparse import *
from .parts import *
import a99
import datetime
import traceback



_python_logger = None
_fmtr = logging.Formatter('[%(levelname)-8s] %(message)s')
def get_python_logger():
    """Returns logger to receive Python messages (as opposed to Fortran).

    Note: we don't want this to be called at any module imports, in order to give the API user a
          chance to set `a99.flag_log_file` and `a99.flag_log_console`
    """
    global _python_logger
    if _python_logger is None:
        fn = "python.log"
        l = logging.Logger("python", level=a99.logging_level)
        if a99.flag_log_file:
            add_file_handler(l, fn)
        if a99.flag_log_console:
            ch = logging.StreamHandler()
            ch.setFormatter(_fmtr)
            l.addHandler(ch)
        _python_logger = l
        for line in a99.format_box("Session started @ {}".format(a99.now_str())):
            l.info(line)
        if a99.flag_log_file:
            l.info("$ Logging to console $")
        if a99.flag_log_file:
            l.info("$ Logging to file '{}' $".format(fn))

    return _python_logger


def add_file_handler(logger, logFilename=None):
    """Adds file handler to logger.

    File is opened in "a" mode (append)
    """
    assert isinstance(logger, logging.Logger)
    ch = logging.FileHandler(logFilename, "a")
    # ch.setFormatter(logging._defaultFormatter) # todo may change to have same formatter as last handler of logger
    ch.setFormatter(_fmtr)
    logger.addHandler(ch)


@froze_it
class LogTwo(object):
  """Logs messages to both stdout and file."""
  def __init__(self, filename):
    self.terminal = sys.stdout
    self.log = open(filename, "w")

  def write(self, message):
    self.terminal.write(message)
    self.log.write(message)

  def close(self):
      self.log.close()


class SmartFormatter(RawDescriptionHelpFormatter):
    """
    Help formatter that will show default option values and also respect
    newlines in description. Neither are done in default help formatter.
    """

    def _get_help_string(self, action):
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not SUPPRESS:
                defaulting_nargs = [OPTIONAL, ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    help += ' (default: %(default)s)'
        return help


        # # this is the RawTextHelpFormatter._split_lines
        # if text.startswith('R|'):
        #     return text[2:].splitlines()
        # return argparse.ArgumentDefaultsHelpFormatter._split_lines(self, text, width)


def str_exc(E):
    """Generates a string from an Exception"""
    return "{0!s}: {1!s}".format(E.__class__.__name__, str(E))
