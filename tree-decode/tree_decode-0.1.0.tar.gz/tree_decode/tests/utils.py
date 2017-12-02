"""
Useful utilities for our tree-decode testing.
"""

import pickle
import sys

PY3 = sys.version_info >= (3, 0, 0)
PY2 = sys.version_info >= (2, 0, 0) and not PY3

if PY3:
    import builtins
else:
    import __builtin__ as builtins


class MockBuffer(object):
    """
    Mock buffer class for testing purposes.
    """

    def __init__(self):
        self.buffer = ""
        self.closed = False

    def read(self):
        return self.buffer

    def write(self, val):
        self.buffer += val

    def close(self):
        self.closed = True


def mock_open(data, filepath):
    """
    An elaborate way to mock built-in functions for our write_to_buf tests.

    The key method we need to override is the `open` function, but only in
    the context of the test and not destroy its meaning outside of it.

    Parameters
    ----------
    data : str
        The data to write to the mock buffer.
    filepath : str
        The filepath that we are using in our tests. The file does not have to
        actually exist in our tests, as that is not the focus here.
    """

    backup = builtins.open
    mock_buffer = MockBuffer()

    def new_open(path, *_):
        assert path == filepath

        new_open.called += 1
        return mock_buffer

    new_open.called = 0

    def wrapper(f):
        def inner_wrapper(*args, **kwargs):
            try:
                builtins.open = new_open
                f(*args, **kwargs)

                assert mock_buffer.buffer == data
                assert new_open.called == 1
                assert mock_buffer.closed
            finally:
                builtins.open = backup

        return inner_wrapper
    return wrapper


def pickle_model(model, filename, **kwargs):
    """
    Pickle a decision-tree model that has compatibility with Python 2.x.

    For the pickling to be compatible, we need to generate the files using
    Python 2.x (hopefully we can use Python 3.x in the future).

    Parameters
    ----------
    model : object
        The decision-tree that we are to pickle.
    filename : str
        The filename where the pickled model is stored.
    """

    if not PY2:
        raise TypeError("Must use Python 2.x to generate pickled files")

    with open(filename, "wb") as f:
        pickle.dump(model, f, protocol=0, **kwargs)


def load_model(filename, **kwargs):
    """
    Unpickle a decision-tree model that has compatibility with Python 2.x.

    Parameters
    ----------
    filename : str
        The filename where the pickled model is stored.

    Returns
    -------
    unpickled_model : object
        The decision-tree model pickled and stored at the given filepath.
    """

    # Encoding argument necessary to read the pickled files.
    if PY3:
        kwargs.update(encoding="latin1")

    with open(filename, "rb") as f:
        return pickle.load(f, **kwargs)
