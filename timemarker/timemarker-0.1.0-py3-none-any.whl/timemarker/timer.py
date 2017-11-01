# -*- coding: utf-8 -*-

import logging
from operator import itemgetter
from typing import List, Tuple, Callable

# TODO(davidr) is it faster to do this here or to save the function as an attribute of the
# class instance?
from timeit import default_timer

_logger = logging.getLogger(__name__)


class TimeMarker(object):
    """Time Marker class

    Todo:
        * how should this behave as a context manager vs. an instantiated object? right now, it
          only works as the former
        * we should support recurring tags (i.e. a timer.tag("foo") inside of a for loop and average
          the time taken for all the calls together, perhaps with stats?
    """

    __slots__ = [
        '_start', '_end', '_tag_timing', '_cumulative_time', '_last_tag',
        '_last_ts'
    ]

    _reserved_tags = ['start', 'stop']
    _stats_formats = ['percentage', 'raw']

    def __init__(self):
        self._start: float = None
        self._end: float = None

        self._tag_timing: List[Tuple[str, float]] = []

        self._cumulative_time: float = None

        self._last_tag: str = None
        self._last_ts: float = None

    def __enter__(self):
        self._start = default_timer()

        # Set up the initial values for our last_* tags
        self._last_ts = self._start
        self._last_tag = 'start'

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tag("stop", _override=True)

        self._end = self._last_ts
        self._cumulative_time = self._end - self._start

    def __repr__(self) -> str:
        return "TimeMarker(start={}, last=({}, {}))".format(
            self._start, self._last_tag, self._last_ts)

    def tag(self, tag: str, _override: bool = False) -> None:
        """Mark a tagged event

        Args:
            tag: name of timer tag
            _override: override checking for reserved tags *Warning: don't use this!*

        Returns:
            None

        Raises:
            ValueError: if given invalid tag name

        """
        if tag in TimeMarker._reserved_tags and _override is False:
            raise ValueError('tag name {} is reserved'.format(tag))

        _ts = default_timer()
        self._cumulative_time = _ts - self._start

        self._tag_timing.append((self._last_tag, _ts - self._last_ts))
        self._last_tag = tag
        self._last_ts = _ts

        _logger.debug("tag took {}".format(default_timer() - _ts))

    def stats(self,
              sort: bool = True,
              fmt: str = "percentage",
              oneline: bool = True,
              print_function: Callable = print,
              pctg_cap: float = 1.):
        """Print out TimeMarker stats

        Args:
            sort: if True, results are sorted by time taken, else in the order in which they were
                tagged
            fmt: format of stats. "raw" is time in seconds, "percentage" is the percentage of the
                total measured time
            oneline: if True, print stats on one line
            print_function: callable with string as only parameter
            pctg_cap: do not print results accounting for more than pctg_cap percentage of the total
                measured time

        Returns:
            None

        """

        if not 0. < pctg_cap <= 1.:
            raise ValueError('pctg must be < 0., <= 1.')
        elif fmt not in TimeMarker._stats_formats:
            raise ValueError('"{:s}" not a valid stats formatter')
        elif pctg_cap < 1. and fmt != "percentage":
            raise ValueError('pctg_cap < 1. requires fmt="percentage"')
        elif pctg_cap < 1. and not sort:
            raise ValueError('pctg_cap < 1. requires sort=True')

        tag_separator = " " if oneline else "\n  - "
        tag_suffix = ""
        stats: List[str] = list()
        tags: List[Tuple[str, float]] = self._tag_timing

        stats.append("TIME:{:.6f}s".format(self._cumulative_time))

        if sort:
            # Sort by the time value of the tag
            tags = sorted(tags, key=itemgetter(1), reverse=True)

        if fmt == "raw":
            tag_suffix = "s"

        elif fmt == "percentage":
            running_pctg = 0.
            tags_pctg: List[Tuple[str, float]] = list()

            for tag, ts in tags:
                tag_pctg = ts / self._cumulative_time

                # if we have a cap of the percentage of time we want accounted for, see if we've
                # gone over
                running_pctg += tag_pctg
                if running_pctg > pctg_cap:
                    break

                tags_pctg.append((tag, tag_pctg))

            tags = tags_pctg

        for tag, duration in tags:
            stats.append("{:s}:{:02.3f}{:s}".format(tag, duration, tag_suffix))

        stats_string = tag_separator.join(stats)
        print_function(stats_string)
