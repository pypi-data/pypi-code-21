from sklearn.tree import DecisionTreeClassifier
from tree_decode.tests import PY3

import tree_decode.utils as utils
import numpy as np
import pytest

if PY3:
    import builtins
else:
    import __builtin__ as builtins


def test_check_estimator_type():
    estimator = DecisionTreeClassifier()
    utils.check_estimator_type(estimator)

    match = "Function support is only implemented for"
    message = "Expected NotImplementedError regarding no support"

    with pytest.raises(NotImplementedError, match=match, message=message):
        utils.check_estimator_type([])


@pytest.mark.parametrize("tab_size", [-5, 0, 2, 5, None])
def test_get_tab(tab_size):
    tab_size = 5 if tab_size is None else max(0, tab_size)
    assert utils.get_tab(tab_size) == " " * tab_size


class TestMaybeRound(object):

    @pytest.mark.parametrize("precision,expected", [(None, 2.05),
                                                    (1, 2.0),
                                                    (5, 2.05)])
    def test_scalar(self, precision, expected):
        scalar = 2.05
        result = utils.maybe_round(scalar, precision=precision)

        assert result == expected

    @pytest.mark.parametrize("precision,expected", [(None, [2.05, 1.072, 3.6]),
                                                    (0, [2.0, 1.0, 4.0]),
                                                    (1, [2.0, 1.1, 3.6]),
                                                    (2, [2.05, 1.07, 3.6]),
                                                    (5, [2.05, 1.072, 3.6])])
    def test_array(self, precision, expected):
        expected = np.array(expected)
        arr = np.array([2.05, 1.072, 3.6])

        result = utils.maybe_round(arr, precision=precision)
        assert np.array_equal(result, expected)


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


class TestWriteToBuf(object):

    data = "example-data"
    filepath = "file-path.txt"

    def test_no_buf(self):
        # Nothing should happen here.
        utils.write_to_buf(self.data, filepath_or_buffer=None)

    def test_actual_buf(self):
        buffer = MockBuffer()
        utils.write_to_buf(self.data, filepath_or_buffer=buffer)

        # Because a buffer was provided, we preserve state
        # and do not close this buffer in this case.
        assert buffer.read() == self.data
        assert not buffer.closed

    @mock_open(data, filepath)
    def test_cat(self):
        utils.write_to_buf(self.data, filepath_or_buffer=self.filepath)
