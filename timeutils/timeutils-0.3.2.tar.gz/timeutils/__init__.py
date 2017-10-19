"""A set of methods and classes to accurately measure elapsed time.

See https://gitlab.com/cmick/timeutils for more information.

Examples
--------

    >>> from timeutils import Stopwatch
    >>> sw = Stopwatch(start=True)
    >>> sw.elapsed_seconds
    16.282313108444214
    >>> str(sw.stop())
    '00:01:30.416'
    >>> sw.elapsed.human_str()
    '1 min, 30 secs'

.. seealso::

    Documentation of the :py:class:`~.stopwatch.Stopwatch` class.
"""
from ._version import __version__

from .stopwatch import Stopwatch


def current_time_millis():
    """Returns the difference, measured in milliseconds, between the current
    time and midnight, January 1, 1970 UTC.
    """
    import time
    return int(round(time.time() * 1000))


def timeit(func, number=1000, repeat=1, args=None, kwargs=None):
    """Measures the execution time of the provided function.

    :param Callable func: function to be executed
    :param int number: number of executions (1000 by default)
    :param int repeat: indicates the number of times the time is measured; if
        greater than 1, a list of results is returned.
    :param tuple,list args: positional arguments to be passed to function `func`
    :param dict[str,Any] kwargs: keyword arguments to be passed to function
        `func`
    :return: measured time, or list of time measurements if `repeat` > 1
    :rtype: TimeSpan or list[TimeSpan]

    .. versionadded:: 0.3.0
    """
    if not isinstance(number, int) and number < 1:
        raise ValueError("repeat must be a positive integer.")
    if not isinstance(repeat, int) and repeat < 1:
        raise ValueError("repeat must be a positive integer.")
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    time_spans = []
    for _ in range(repeat):
        sw = Stopwatch(start=True)
        for _ in range(number):
            func(*args, **kwargs)
        sw.stop()
        time_spans.append(sw.elapsed)
    if len(time_spans) == 1:
        return time_spans[0]
    return time_spans
