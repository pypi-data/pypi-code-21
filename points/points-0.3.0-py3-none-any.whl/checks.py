"""Contains functions for checking certain properties of numbers and numerical
obects."""

def is_numeric(number):
    """Checks if an object is a number. That is, a ``float`` or an ``int``.
    Where this differs from simply checking if an object is an instance of
    ``numbers.Number`` is that boolean objects are also a number by that
    measure (which, technically,
    `they are <https://www.peterbe.com/plog/bool-is-int>`_). While technical
    correctness is a wonderful thing, generally this is not what one would
    expect a check for numbers to do.

    :param Number: The object to check.
    :rtype: ``bool``"""

    if isinstance(number, bool):
        return False
    elif isinstance(number, int) or isinstance(number, float):
        return True
    else:
        return False


def are_numeric(*values):
    """Checks if all the arguments it receives are numeric (according to
    :py:func:`is_numeric`).

    :param \*values: The objects to check.
    :rtype: ``bool``"""

    for value in values:
        if not is_numeric(value):
            return False
    return True
