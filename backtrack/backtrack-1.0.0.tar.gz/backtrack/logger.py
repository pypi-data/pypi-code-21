import datetime
import inspect
import os
import sys
import time

# Logging levels
INFO = 0
WARNING = 1
ERROR = 2

# ANSI color codes
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

# Don't touch!
fd = sys.stdout
level_ = 0
color = False


def _get_file():
    frame = inspect.currentframe()
    try:
        frame = frame.f_back
    except AttributeError:
        pass
    while hasattr(frame, "f_code"):
        code = frame.f_code
        filename = os.path.normcase(code.co_filename)
        if filename != __file__:
            break
        frame = frame.f_back
    return filename


def configure(file_descriptor=sys.stdout, level=INFO, use_color=False):
    """Set logging options.
    Parameters:
        * file_descriptor: A file descriptor with a 'write' method.
          Defaults to sys.stdin.
        * level: An integer (any of 0, 1, 2 for INFO, WARNING and ERROR
          respectively). Defaults to INFO.
        * use_color: Whether or not to use ANSI color codes. Defaults to False.
    Returns:
        * None
    Raises:
        * RuntimeError if 'file_descriptor' has no 'write' method.
        * ValueError if 'level' is not any of INFO, WARNING, ERROR.
    """
    if not hasattr(file_descriptor, "write"):
        raise RuntimeError("Passed a file descriptor with no 'write' method")
    global fd
    fd = file_descriptor

    if level not in {INFO, WARNING, ERROR}:
        raise ValueError("'level' must be any of INFO, WARNING, ERROR")
    global level_
    level_ = level
    global color
    color = use_color


def error(message):
    """Write a level 2 (ERROR) message to the file."""
    _write(ERROR, message=message)


def _format_message(message):
    return message.format(
        datetime=time.ctime(),
        file=_get_file(),
        unixtime=time.time()
    )


def info(message):
    """Write a level 0 (INFO) message to the file."""
    _write(INFO, message=message)


def warning(message):
    """Write a level 1 (WARNING) message to the file."""
    _write(WARNING, message=message)


def _write(level, message):
    if level < level_:
        return
    if level == INFO:
        if color:
            fd.write(GREEN)
        prefix = "[Info] "
    elif level == WARNING:
        if color:
            fd.write(YELLOW)
        prefix = "[Warning] "
    else:
        if color:
            fd.write(RED)
        prefix = "[Error] "
    fd.write(prefix + _format_message(message=message))
    if color:
        fd.write(RESET)
    fd.write("\n")

for function in {info, warning, error}:
    function.__doc__ += """ Valid formatting keys:
    {datetime}: The date and time as reported by 'time.ctime'.
    {unixtime}: The unix timestamp as reported by 'time.time'.
    {file}: The calling file.
    """
del function
