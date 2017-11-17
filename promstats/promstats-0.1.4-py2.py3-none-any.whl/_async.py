import time


from ._timer import Timer


class AsyncTimer(Timer):
    """A timer instance, which awaits the wrapped function."""

    def _wrapped_factory(self, func):
        """Report an execution time for each function run.

        :param func (function): A function to wrap for measurement.
        :returns function: A measured function, which will be awaited.
        """
        async def wrapped(*args, **kwargs):
            self.time_start = time.time()
            ret = await func(*args, **kwargs)
            self.__exit__(None, None, None)
            return ret

        return wrapped
