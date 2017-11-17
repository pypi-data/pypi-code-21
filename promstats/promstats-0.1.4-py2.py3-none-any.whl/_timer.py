from functools import wraps
import time

from ._util import maybe_labels


class Timer:
    """A Timer instance for instrumenting function runs,
        or arbitrary pieces of code.

    Usage:
        stats = Stats('greasyspoon')
        with stats.timed(
            'eggs',
            tags=['spam:ham'],
            verbose_name='Number of eggs in a basket.'):
            ... your code here ...
    """

    def _wrapped_factory(self, func):
        """Report an execution time for each function run.

        :param func (function): A function to wrap for measurement.
        :returns function: A measured function.
        """

        self.func = func

        @wraps(func)
        def wrapped(*args, **kwargs):
            self.time_start = time.time()
            ret = func(*args, **kwargs)
            self.__exit__(None, None, None)
            return ret

        return wrapped

    def __init__(self, metric, tags=()):
        self.metric = metric
        self.tags = tags
        self.time_start = None
        self.func = None

    def __repr__(self):
        s = '{}'.format(self.__class__.__name__)
        if self.time_start:
            s = '{}<{}>'.format(s, str(time.time() - self.time_start))
        if self.func:
            s = '{}[{}]'.format(s, self.func.__name__)
        return s

    def __call__(self, func):
        return self._wrapped_factory(func)

    def __enter__(self):
        self.time_start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        maybe_labels(self.metric, self.tags)\
            .observe(time.time() - self.time_start)
