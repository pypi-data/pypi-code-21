"""Provides File Logger class."""
import sys
import time
import os


def currentframe():
    """Return the frame object for the caller's stack frame."""
    try:
        raise Exception
    except:  # noqa
        return sys.exc_info()[2].tb_frame.f_back


_srcfile = os.path.normcase(currentframe.__code__.co_filename)


def find_caller():
    """Find the caller on the stack frame."""
    f = currentframe()
    if f is not None:
        f = f.f_back
    rv = "(unknown file)", 0, "(unknown function)"
    while hasattr(f, "f_code"):
        co = f.f_code
        filename = os.path.normcase(co.co_filename)
        if filename == _srcfile:
            f = f.f_back
            continue
        rv = (co.co_filename, f.f_lineno, co.co_name)
        break
    return rv


class FileLogger(object):
    """File Logger class."""

    def __init__(self, fd):
        """Initialize FileLogger object with File Descriptor."""
        self._fd = fd

    def __call__(self, msg):
        """Log the message."""
        if self._fd and not self._fd.closed:
            ct = time.time()
            msecs = (ct - long(ct)) * 1000
            pathname, lineno, name = find_caller()
            try:
                mod = os.path.splitext(".".join(map(os.path.basename, os.path.split(pathname))))[:-1][0]
            except (TypeError, ValueError, AttributeError):
                mod = "Unknown module"
            ts = time.strftime("%Y-%m-%d %H:%M:%S", (time.localtime(ct)))
            self._fd.write("%s,%03d %s:%s(%s): %s\n" % (ts, msecs, mod, name, lineno, msg))
            self._fd.flush()
