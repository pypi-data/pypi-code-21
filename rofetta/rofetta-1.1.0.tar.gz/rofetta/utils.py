
import os
import tempfile
from functools import wraps


def format_from_filename(fname:str) -> str or None:
    """Return the format associated with given filename"""
    return os.path.splitext(fname)[1][1:]
def basename_from_filename(fname:str) -> str or None:
    """Return the format associated with given filename"""
    return os.path.splitext(fname)[0]


def output_as_tempfile(func):
    """Make conversion functions working with only input file, and returning
    their output (temp)file.

    """
    @wraps(func)
    def wrapper(fin, fout=None):
        if not fout:
            with tempfile.NamedTemporaryFile('w', delete=False) as fd:
                fout = fd.name
        func(fin, fout)
        return fout
    return wrapper
