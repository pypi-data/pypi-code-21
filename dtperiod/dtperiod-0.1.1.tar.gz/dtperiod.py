
try:
    from collections.abc import Mapping
except ImportError:
    try:
        from collections import Mapping
    except ImportError:
        raise ImportError('Python version must be 2.4+ or 3.3+')
from datetime import date, timedelta
from copy import deepcopy


__version__ = '0.1.1'
__all__ = ['Period']


class Period(Mapping):
    # TODO implement __format__ special method
    # TODO consider to implement comparison special methods
    # TODO add pydoc

    __slots__ = ('_start', '_stop')

    def __init__(self, start, stop_or_delta):
        start = deepcopy(start)
        if isinstance(stop_or_delta, timedelta):
            delta = stop_or_delta
            stop = start + delta
        else:
            stop = deepcopy(stop_or_delta)
        self._start = start
        self._stop = stop

    @property
    def start(self):
        return deepcopy(self._start)

    @property
    def stop(self):
        return deepcopy(self._stop)

    @property
    def delta(self):
        return self._stop - self._start

    def overlap_with(self, other):
        return isinstance(other, Period) and any([
            other._start in self,
            self._start in other,
        ])

    @property
    def _tuple(self):
        return (self._start, self._stop)

    def __repr__(self):
        try:
            cls_name = Period.__qualname__
        except AttributeError:
            cls_name = Period.__name__
        return '{module}.{cls}(start={start!r}, stop={stop!r})'.format(
            module=Period.__module__,
            cls=cls_name,
            start=self._start,
            stop=self._stop,
        )

    def __str__(self):
        return '{start} -> {stop}'.format(start=self._start, stop=self._stop)

    def __eq__(self, other):
        return isinstance(other, Period) and self._tuple == other._tuple

    def __hash__(self):
        return hash(self._tuple)

    def __len__(self):
        return 3

    def __iter__(self):
        return iter((self.start, self.stop, self.delta))

    def __getitem__(self, key):
        if key in ('start', 'stop', 'delta'):
            return getattr(self, key)
        else:
            raise KeyError(key)

    def __contains__(self, key):
        if isinstance(key, date):
            return any([
                self._start <= key < self._stop,
                self._start >= key > self._stop,
            ])
        elif isinstance(key, Period):
            return all([
                key._start in self,
                any([
                    self._start < key._stop <= self._stop,
                    self._start > key._stop >= self._stop,
                ]),
            ])
        else:
            return super().__contains__(key)
