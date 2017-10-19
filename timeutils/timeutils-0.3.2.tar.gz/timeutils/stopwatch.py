"""Stopwatch"""
# Author: Michal Ciesielczyk
# Licence: MIT
import time
import sys

from datetime import datetime

from .timespan import TimeSpan


class Stopwatch:
    """Provides a set of methods and properties that you can use to accurately
    measure elapsed time.

    :param start: if set to `True`, immediately starts measuring the time
        (by calling :py:meth:`~.stopwatch.Stopwatch.start`). By default set to
        `False`.
    :type start: bool, optional
    :param verbose: if set to `True`, logs the elapsed time when the
        :py:meth:`~.stopwatch.Stopwatch.stop` method is called. By default set
        to `False`.
    :type verbose: bool, optional
    :param label: Optional stopwatch label to be included in the log messages
        (only if `verbose` is `True`).
    :type label: str, optional
    :param logger: logger object for logging stopwatch messages if `verbose` is
        `True`. If set to `None` (the default), the logger is set to
        :py:obj:`python:sys.stdout`.
    :type logger: :py:class:`python:logging.Logger`, optional
    :param logger_level: logging level as defined in the build-in `logging
        <https://docs.python.org/3/library/logging.html#logging-levels>`_
        package (only if the `logger` object is set).
    :type logger_level: int, optional

    .. rubric:: Examples

    Simple time measurement::

        sw = Stopwatch(start=True)
        # code to be measured
        sw.stop()

    Getting the elapsed time::

        print(sw.elapsed)  # hh:mm:ss.ms
        print(sw.elapsed.human_str())  # human-readable time

    Restarting the stopwatch instance::

        sw.restart()

    Pausing and resuming the stopwatch::

        sw.suspend()
        # code block not included in the measurement
        sw.resume()

    Using a logger::

        import logging

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.FileHandler(filename='example.log'))

        sw = Stopwatch(verbose=True, label='Example', logger=logger)
        sw.start()
        # code to be measured
        sw.stop()

    .. note::

        :py:class:`~.stopwatch.Stopwatch` methods are protected against
        inappropriate calls. It is an error to start or stop a
        :py:class:`~.stopwatch.Stopwatch` object that is already in the desired
        state.

    .. seealso::

        Documentation of the :py:class:`~.timespan.TimeSpan` class.
    """

    def __init__(self, start=False, verbose=False, label=None, logger=None,
                 logger_level=None):
        """Creates a new :py:class:`~.stopwatch.Stopwatch` instance."""
        self._label = "Stopwatch" if label is None else label
        self.__elapsed = 0
        self.__stop_time = None
        if verbose:
            if logger is None:
                log = sys.stdout.write
            elif logger_level is None:
                log = logger.info
            else:
                def log(*args, **kwargs):
                    logger.log(logger_level, *args, **kwargs)
        else:
            def log(*args, **kwargs):
                pass  # do-nothing function
        self.__log = log
        self.__start_time = time.time() if start else None
        self.__last_resume = self.__start_time

    @property
    def is_running(self):
        """Indicates whether the :py:class:`~.stopwatch.Stopwatch` instance is
        running.
        """
        return self.__start_time is not None and self.__stop_time is None

    def start(self):
        """Starts measuring elapsed time for an interval."""
        assert not self.is_running, "Stopwatch is already running."
        assert self.__elapsed == 0, "Stopwatch has already been executed."
        self.__start_time = time.time()
        self.__last_resume = self.__start_time

    def reset(self):
        """Stops time interval measurement and resets the
        :py:class:`~.stopwatch.Stopwatch` instance. The time elapsed before
        reset is set to zero.
        """
        self.__elapsed = 0
        self.__start_time = None
        self.__stop_time = None
        self.__last_resume = None

    @property
    def is_suspended(self):
        """Indicates whether the :py:class:`~.stopwatch.Stopwatch` instance is
        suspended.
        """
        return self.__last_resume is None

    def suspend(self):
        """Pauses the time measurement until the
        :py:class:`~.stopwatch.Stopwatch` instance is resumed or stopped.
        Returns the total elapsed time measured by the current instance.

        Call :py:meth:`~.stopwatch.Stopwatch.resume` to resume measuring
        elapsed time.
        """
        assert self.is_running, "Stopwatch is already stopped."
        assert not self.is_suspended, "Stopwatch is already suspended."
        self.__elapsed += time.time() - self.__last_resume
        self.__last_resume = None
        return self.elapsed

    def resume(self):
        """Resumes measuring elapsed time after calling
        :py:meth:`~timeutils.stopwatch.Stopwatch.suspend`.
        """
        assert self.is_running, "Stopwatch is already stopped."
        assert self.is_suspended, "Stopwatch is not suspended."
        self.__last_resume = time.time()

    def stop(self):
        """Stops the time measurement. Returns the total elapsed time measured
        by the current instance.
        """
        assert self.is_running, "Stopwatch is already stopped."
        self.__stop_time = time.time()
        if not self.is_suspended:
            self.__elapsed += self.__stop_time - self.__last_resume
            self.__last_resume = None
        self.__log("{} - elapsed time: {}".format(self._label, self.elapsed))
        return self.elapsed

    def restart(self):
        """Stops time interval measurement, resets the
        :py:class:`~.stopwatch.Stopwatch` instance, and starts measuring
        elapsed time. The time elapsed before restart is set to zero.
        """
        self.stop()
        self.reset()
        self.start()

    @property
    def elapsed_seconds(self):
        """The total elapsed time in fractions of a second measured by the
        current instance.
        """
        if self.is_running and not self.is_suspended:
            return self.__elapsed + time.time() - self.__last_resume
        else:
            return self.__elapsed

    @property
    def elapsed(self):
        """The total elapsed time measured by the current instance."""
        return TimeSpan(seconds=self.elapsed_seconds)

    def __float__(self):
        return self.elapsed_seconds

    @property
    def start_time(self):
        """The datetime at which the time measurement has been started.

        .. versionchanged:: 0.3.2
            Returns a datetime object instead of a float timestamp.
        """
        assert self.__start_time is not None, \
            "The Stopwatch hasn't been started."
        return datetime.fromtimestamp(self.__start_time)

    @property
    def stop_time(self):
        """The datetime at which the time measurement has been stopped.

        .. versionchanged:: 0.3.2
            Returns a datetime object instead of a float timestamp.
        """
        assert self.__stop_time is not None, \
            "Stopwatch hasn't been stopped yet."
        return datetime.fromtimestamp(self.__stop_time)

    def __str__(self):
        return str(self.elapsed)

    def __enter__(self):
        self.start()

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()
