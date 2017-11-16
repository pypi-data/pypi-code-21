from __future__ import absolute_import, division
import chainlet
import logging
import time
import numbers
import math
import collections


class WindowedInterval(numbers.Real):
    """

    """
    def __init__(self, window=3600.):
        self.window = window
        self._buffer = collections.deque()

    @property
    def _mean(self):
        return sum(self._buffer)

    def push(self):
        now = time.time()


    def __str__(self):
        if self._mean == 0 or self._half_life_count == 0.0:
            return "-.-- +/ -.-- [-.--]"
        weight = 2 ** (-(time.time() - self._last_update) / self.half_life)
        return '%.2g +/- %.2g [%.2g]' % (self._mean * weight, self._stdev * weight, weight * self.half_life / self._half_life_count)

    def __repr__(self):
        return '%s(half_file=%f, mean=%f, stdev=%f, last=%f)' % (
            self.__class__.__name__, self.half_life, self._mean, self._stdev, self._last_update
        )

    def __float__(self):
        return self._mean

    def __abs__(self):
        return abs(self._mean)

    def __add__(self, other):
        return self._mean + other

    def __radd__(self, other):
        return other + self._mean

    def __sub__(self, other):
        return self._mean - other

    def __ceil__(self):
        return ceil(self._mean)

    def __eq__(self, other):
        return self._mean == other

    def __floor__(self):
        return floor(self._mean)

    def __round__(self, n=None):
        return round(self, n)

    def __trunc__(self):
        return trunc(self)

    def __truediv__(self, other):
        return self._mean / other

    def __rtruediv__(self, other):
        return other / self._mean

    def __floordiv__(self, other):
        return self._mean // other

    def __rfloordiv__(self, other):
        return other // self._mean

    def __le__(self, other):
        return self._mean <= other

    def __lt__(self, other):
        return self._mean < other

    def __mod__(self, other):
        return self._mean % other

    def __rmod__(self, other):
        return other % self._mean

    def __mul__(self, other):
        return self._mean * other

    def __rmul__(self, other):
        return other * self._mean

    def __neg__(self):
        return -self._mean

    def __pos__(self):
        return +self._mean

    def __pow__(self, power, modulo=None):
        return pow(self._mean, power, modulo)

    def __rpow__(self, other):
        return other ** self._mean


class DecayingInterval(numbers.Real):
    """

    """
    def __init__(self, half_life=3600.):
        self.half_life = half_life
        self._last_update = float('nan')
        self._mean = 0.0
        self._stdev = 0.0
        self._initialized = 0.0
        self._half_life_count = 0.0

    def push(self, now=None):
        if now is None:
            now = time.time()
        if self._initialized == 0.0:
            return self._push_initialize(now)
        elif now < self._initialized:
            half_life = now - self._initialized + self.half_life
        else:
            half_life = self.half_life
        mean, stdev, last_update, half_life_count = self._mean, self._stdev, self._last_update, self._half_life_count
        this_interval = now - last_update
        this_count = half_life / this_interval
        weight_old = 2 ** (-this_interval / half_life)
        delta = this_interval - mean
        print('m%5.3f w%5.3f i%5.3f h%5.3f -- h%5.3f t%5.3f' % (mean, weight_old, this_interval, half_life, half_life_count, this_count))
        mean = mean * weight_old + this_interval * (1 - weight_old)
        count = half_life_count * weight_old + this_count * (1 - weight_old)
        delta2 = this_interval - mean
        stdev = stdev * weight_old + delta * delta2 * (1 - weight_old)
        self._mean, self._stdev, self._last_update, self._half_life_count = mean, stdev, now, count

    def _push_initialize(self, now):
        if not math.isnan(self._last_update):
            self._mean = now - self._last_update
            self._initialized = time.time() + self.half_life
        self._last_update = now
        return

    def _push_early(self, now):
        effective_half_life = now - self._initialized + self.half_life
        current_interval = now - self._last_update
        weight_old = 2 ** (-current_interval / effective_half_life)

    def __str__(self):
        if self._mean == 0 or self._half_life_count == 0.0:
            return "-.-- +/ -.-- [-.--]"
        weight = 2 ** (-(time.time() - self._last_update) / self.half_life)
        return '%.2g +/- %.2g [%.2g]' % (self._mean * weight, self._stdev * weight, weight * self.half_life / self._half_life_count)

    def __repr__(self):
        return '%s(half_file=%f, mean=%f, stdev=%f, last=%f)' % (
            self.__class__.__name__, self.half_life, self._mean, self._stdev, self._last_update
        )

    def __float__(self):
        return self._mean

    def __abs__(self):
        return abs(self._mean)

    def __add__(self, other):
        return self._mean + other

    def __radd__(self, other):
        return other + self._mean

    def __sub__(self, other):
        return self._mean - other

    def __ceil__(self):
        return ceil(self._mean)

    def __eq__(self, other):
        return self._mean == other

    def __floor__(self):
        return floor(self._mean)

    def __round__(self, n=None):
        return round(self, n)

    def __trunc__(self):
        return trunc(self)

    def __truediv__(self, other):
        return self._mean / other

    def __rtruediv__(self, other):
        return other / self._mean

    def __floordiv__(self, other):
        return self._mean // other

    def __rfloordiv__(self, other):
        return other // self._mean

    def __le__(self, other):
        return self._mean <= other

    def __lt__(self, other):
        return self._mean < other

    def __mod__(self, other):
        return self._mean % other

    def __rmod__(self, other):
        return other % self._mean

    def __mul__(self, other):
        return self._mean * other

    def __rmul__(self, other):
        return other * self._mean

    def __neg__(self):
        return -self._mean

    def __pos__(self):
        return +self._mean

    def __pow__(self, power, modulo=None):
        return pow(self._mean, power, modulo)

    def __rpow__(self, other):
        return other ** self._mean


@chainlet.genlet
def frequency(half_life=10, logger=logging.getLogger('%s.frequency' % __name__)):
    """
    Track and report the frequency of data chunks

    :param every: how many seconds to wait between reports
    :param logger: the logger to use for reporting
    :type logger: logging.Logger
    :return:
    """
    chunk = yield
    while True:
        chunk = yield chunk

import random
interval = DecayingInterval(half_life=25)
actual = []
multiplier = 2
print('expect:', multiplier * 0.5)
for idx in range(50):
    sleep_for = random.random() * multiplier
    actual.append(sleep_for)
    time.sleep(sleep_for)
    interval.push()
    mean = sum(actual) / len(actual)
    timew = sum(val**2 for val in actual) / sum(actual)
    print('    ', idx, interval, 'm%.2g' % mean, 'd%.2g' % abs(interval - mean), 't%.2g' % timew, 'd%.2g' % abs(interval - timew))
print('expect:', multiplier * 0.5)
