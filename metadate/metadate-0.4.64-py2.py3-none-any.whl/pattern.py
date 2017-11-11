from itertools import product
from collections import Counter
from metadate.classes import MetaAnd
from metadate.classes import MetaEvery
from metadate.classes import MetaDate
from metadate.classes import MetaOrdinal
from metadate.classes import MetaUnit
from metadate.classes import MetaPeriod
from metadate.classes import MetaDuration
from metadate.classes import MetaModifier
from metadate.classes import MetaRange
from metadate.classes import MetaRelative
from metadate.classes import Meta
from metadate.classes import MetaBetween


def is_instance(instances):
    def fn(x):
        return isinstance(x, instances)
    return fn


def not_is_instance(instances):
    def fn(x):
        return not isinstance(x, instances)
    return fn


def attr_equal_to(attr, value):
    def fn(x):
        return getattr(x, attr, None) == value
    return fn


def x_equal_to(value):
    def fn(x):
        return getattr(x, "x", None) == value
    return fn


class PatternScanner():

    def __init__(self, patterns):
        self.patterns = self.build_list(patterns)

    def scan(self, ls):
        n = len(ls)
        matches = []
        used = set()
        for pattern, pattern_fn in self.patterns:
            lp = len(pattern)
            for offset in range(0, n - lp + 1):
                small_matches = []
                i = 0
                p = 0
                trues = Counter()
                while i + offset < n and p < lp:
                    token = ls[i + offset]
                    if pattern[p](token):
                        trues[p] += 1
                        i += 1
                        small_matches.append(token)
                    elif p in trues:
                        p += 1
                    else:
                        break
                if all([trues[x] for x in range(len(pattern))]):
                    if not used.intersection(small_matches):
                        matches.append(pattern_fn(small_matches))
                        used.update(small_matches)
        return sorted(matches, key=lambda x: x[0].span)

    @staticmethod
    def build_list(lop):
        processed_list = []
        for x, fn in lop:
            inner_list = []
            for y in x:
                if isinstance(y, type):
                    inner_list.append(is_instance(y))
                elif isinstance(y, tuple):
                    inner_list.append(is_instance(y))
                else:
                    inner_list.append(y)
            processed_list.append((inner_list, fn))
        return processed_list


def scan_product(*args, fn=None):
    if fn is None:
        return [sum(list(x), []) for x in product(*args)]
    else:
        return [(sum(list(x), []), fn) for x in product(*args)]


ord_unit = [MetaOrdinal, MetaUnit]
a_unit = [MetaUnit]
more_units = [(MetaUnit, MetaOrdinal, MetaAnd)]
between_date_and_ordinal = [MetaBetween, MetaDate, MetaAnd, MetaOrdinal]
between_date_and_date = [MetaBetween, MetaDate, MetaAnd, MetaDate]
between_modunit_and_mod = [MetaBetween, MetaModifier, MetaUnit, MetaAnd, MetaModifier]
and_rd_rd = [MetaRelative, MetaAnd, MetaRelative]
units = scan_product([ord_unit, a_unit], [more_units, []])


def self(x):
    return x

patterns = scan_product([[MetaDuration]], units, fn=self)
patterns += scan_product([[MetaEvery]], units, fn=self)
patterns += [(and_rd_rd, self)]
patterns += [
    (between_date_and_ordinal, self),
    (between_date_and_date, self),
    (between_modunit_and_mod, self)
]

pattern_scanner = PatternScanner(patterns)
