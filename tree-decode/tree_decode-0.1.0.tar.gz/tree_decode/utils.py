"""
Useful utilities for our tree-decoding API.
"""

from sklearn.tree import DecisionTreeClassifier


def check_estimator_type(estimator):
    """
    Check that the data type of estimator is one that we support.

    Currently, we only support `sklearn.tree.DecisionTreeClassifier`,
    though support for other trees is forthcoming.

    Parameters
    ----------
    estimator : object
        The estimator to check.

    Raises
    ------
    NotImplementedError : the data type of the estimator was one that
                          we do not support at the moment.
    """

    if not isinstance(estimator, DecisionTreeClassifier):
        raise NotImplementedError("Function support is only implemented for "
                                  "DecisionTreeClassifier. Support for "
                                  "other trees is forthcoming.")


def get_tab(size=5):
    """
    Get a tab composed of a given number of spaces.

    Parameters
    ----------
    size : int, default 5
        The number of spaces to use for a tab.

    Returns
    -------
    tab_str : str
        The provided tab to a given number of spaces.
    """

    return " " * size


def maybe_round(val, precision=None):
    """
    Potentially round a number or an array of numbers to a given precision.

    Parameters
    ----------
    val : numeric or numpy.ndarray
        The number or array of numbers to round.
    precision : int, default None
        The precision at which to perform rounding. If None is provided,

    Returns
    -------
    maybe_rounded_val : the number or array of numbers rounded to a
                        given precision, if provided. Otherwise, the
                        original input is returned.
    """

    if precision is None:
        return val

    if hasattr(val, "round"):
        return val.round(precision)
    else:
        return round(val, precision)


def write_to_buf(output, filepath_or_buffer=None):
    """
    Write output to a file or buffer. If none is provided, nothing happens.

    Parameters
    ----------
    output : str
        The output to write.
    filepath_or_buffer : str or file handle, default None
        The file or buffer to which to write the output.
    """

    if filepath_or_buffer is None:
        return

    # We want to preserve state when writing to a buffer.
    # If a buffer was provided, we don't close it. If a
    # path is provided, we close the file buffer once we
    # finish writing to the given filepath.
    if isinstance(filepath_or_buffer, str):
        f = open(filepath_or_buffer, "w")
        close_file = True
    else:
        f = filepath_or_buffer
        close_file = False

    try:
        f.write(output)
    finally:
        if close_file:
            f.close()
