import sys


class DoesNotExist(Exception):
    pass


class InvalidState(Exception):
    pass


class APIError(IOError):
    pass


def reraise(exc_type):
    """
    Reraise the current exception (from `sys.exc_info`), but change its type
    to the specified type.  The message and traceback from the current
    exception are retained.
    """
    _, value, traceback = sys.exc_info()
    raise exc_type, value, traceback
