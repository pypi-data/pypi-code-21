from functools import wraps
from paramdec import paramdec


START_DEFAULT = END_DEFAULT = ""


@paramdec
def stringwrap(func, start=START_DEFAULT, end=END_DEFAULT):
    @wraps(func)
    def wrapper(*func_args, **func_kwargs):
        return "%s%s%s" % (start, func(*func_args, **func_kwargs), end)
    return wrapper
