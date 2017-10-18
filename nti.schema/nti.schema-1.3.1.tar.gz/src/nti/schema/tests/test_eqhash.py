#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""


"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import unittest
from hamcrest import assert_that
from hamcrest import is_
from hamcrest import is_not
from hamcrest import calling
from hamcrest import raises

from ..eqhash import EqHash
from nti.schema.schema import _superhash as superhash # make sure works

@EqHash('a', 'b')
class Thing(object):
    a = 'a'
    b = 'b'

@EqHash('a', 'b', superhash=True)
class Thing2(object):
    a = 'a'
    b = 'b'

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

@EqHash('a', 'b', include_type=True)
class NotThing(object):
    a = 'a'
    b = 'b'

@EqHash('c', include_super=True)
class ChildThing(Thing):
    c = 'c'

@EqHash('c', include_super=False)
class ChildThingNoSuper(Thing):
    c = 'c'

@EqHash(include_super=True)
class ChildThingNoNames(Thing):
    pass

@EqHash('a', 'b', 'c', 'd', 'e', 'f')
class ManyThing(object):
    a = 'a'
    b = 'b'
    c = 'c'
    d = 'd'
    e = 'e'
    f = 'f'

class TestEqHash(unittest.TestCase):

    def test_eq_hash(self):

        thing1 = Thing()
        thing2 = Thing()

        assert_that(thing1, is_(thing1)) # self
        assert_that(thing1, is_(thing2)) # commutative
        assert_that(thing2, is_(thing1))
        assert_that(hash(thing1), is_(hash(thing2)))

        assert_that(thing1, is_not(self)) # missing attr

        thing2.b = 'B'

        assert_that(thing1, is_not(thing2))
        assert_that(hash(thing1), is_not(hash(thing2)))

        # hamcrest calls == even for is_not
        assert thing1 != thing2
        assert thing1 != self # NotImplemented

    def test_eq_hash_mutates(self):

        thing_nosuperhash = Thing()
        thing_superhash = Thing2() # initially, no superhashing required

        assert_that(hash(thing_nosuperhash), is_(hash(thing_superhash)))

        # Ok, mutate one of the attributes to require superhashing
        thing_superhash.a = [1, 2]
        assert_that(hash(thing_superhash), is_(hash(thing_superhash)))

        thing_superhash2 = Thing2()
        thing_superhash2.a = [1, 2]
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))
        # And again, to prove we don't change unnecessarily
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))
        # But we can mutate the other attribute and we will change
        # hash strategies
        thing_superhash.b = {}
        thing_superhash2.b = {}
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))

        # OK, now that we've mutated, mutate again to something that's
        # not a dictionary, but is hashable and isn't iterable.
        class AThing(object):
            pass
        athing = AThing()
        hash(athing)
        thing_superhash.b = athing
        thing_superhash2.b = athing
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))

        # One more mutation for coverage
        thing_superhash.a = athing
        thing_superhash2.a = athing
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))
        assert_that(hash(thing_superhash2), is_(hash(thing_superhash)))


    def test_eq_hash_classes(self):
        # Default doesn't include classes

        assert_that(Thing(), is_(Thing2()))
        assert_that(hash(Thing()), is_(hash(Thing2())))

        # We can ask for it, but note that the order of arguments
        # matters
        assert_that(Thing(), is_(NotThing()))
        assert_that(NotThing(), is_not(Thing()))

    def test_eq_hash_super(self):
        thing1 = ChildThing()
        thing2 = ChildThing()

        assert_that(thing1, is_(thing2))

        assert_that(hash(thing1), is_(hash(thing2)))

        thing1.a = 'A'
        assert_that(thing1, is_not(thing2))
        assert_that(hash(thing1), is_not(hash(thing2)))

        thing3 = ChildThingNoNames()
        thing4 = ChildThingNoNames()
        assert_that(thing3, is_(thing4))
        assert_that(hash(thing3), is_(hash(thing4)))

    def test_eq_hash_no_super(self):
        thing1 = ChildThingNoSuper()
        thing2 = ChildThingNoSuper()

        assert_that(thing1, is_(thing2))
        assert_that(hash(thing1), is_(hash(thing2)))

        thing1.a = 'A'
        assert_that(thing1, is_(thing2))
        assert_that(hash(thing1), is_(hash(thing2)))

        thing1.c = 'C'
        assert_that(thing1, is_not(thing2))
        assert_that(hash(thing1), is_not(hash(thing2)))

    def test_bad_construct(self):
        assert_that(calling(EqHash), raises(TypeError, "Asking to hash"))
        assert_that(calling(EqHash).with_args(foo=True),
                    raises(TypeError, "Unexpected keyword"))



class TestSuperHash(unittest.TestCase):

    def test_iterable(self):
        assert_that(hash(superhash([1, 3, 5])),
                    is_(hash(superhash([x for x in [1, 3, 5]]))))

        assert_that(superhash([1, 2]), is_not(superhash([2, 1])))
        assert_that(hash(superhash([1, 2])), is_not(hash(superhash([2, 1]))))

    def test_nested_dict(self):
        d = {1: 1,
             2: [1, 2, 3],
             3: {4: [4, 5, 6]}}

        assert_that(superhash(d),
                    is_(
                        ((1, 1),
                         (2, (1, 2, 3)),
                         (3, ((4, (4, 5, 6)),)))
                    ))

        assert_that(hash(superhash(d)),
                    is_(-6213620179105025536))


def bench_hash(): # pragma: no cover
    import timeit
    import statistics


    timer = timeit.Timer('hash(thing)', 'from nti.schema.tests.test_eqhash import Thing as Thing; thing=Thing()')
    times = timer.repeat()
    print("Avg Base  hash", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('hash(thing)', 'from nti.schema.tests.test_eqhash import ChildThing as Thing; thing=Thing()')
    times = timer.repeat()
    print("Avg Child hash", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('hash(thing)', 'from nti.schema.tests.test_eqhash import Thing2 as Thing; thing=Thing()')
    times = timer.repeat()
    print("Avg Super  hash", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('hash(thing)', 'from nti.schema.tests.test_eqhash import Thing2 as Thing; thing=Thing(a={})')
#    import cProfile
#    import pstats
#    pr = cProfile.Profile()
#    pr.enable()
    times = timer.repeat()
#    pr.disable()
#    ps = pstats.Stats(pr).sort_stats('cumulative')
#    ps.print_stats(.4)

    print("Avg Super2  hash", statistics.mean(times), "stddev", statistics.stdev(times))


def bench_eq(): # pragma: no cover
    import timeit
    import statistics


    timer = timeit.Timer('thing == thing2', 'from nti.schema.tests.test_eqhash import Thing as Thing; thing=Thing(); thing2 = Thing()')
    times = timer.repeat()
    print("Avg Base  eq", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('thing == thing2', 'from nti.schema.tests.test_eqhash import ChildThing as Thing; thing=Thing(); thing2 = Thing()')
    times = timer.repeat()
    print("Avg Child eq", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('thing == thing2', 'from nti.schema.tests.test_eqhash import Thing2 as Thing; thing=Thing(); thing2 = Thing()')
    times = timer.repeat()
    print("Avg Super  eq", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('thing == thing', 'from nti.schema.tests.test_eqhash import Thing2 as Thing; thing=Thing(a={}); thing2 = Thing(a={})')
#    import cProfile
#    import pstats
#    pr = cProfile.Profile()
#    pr.enable()
    times = timer.repeat()
#    pr.disable()
#    ps = pstats.Stats(pr).sort_stats('cumulative')
#    ps.print_stats(.4)




    print("Avg Super2  eq", statistics.mean(times), "stddev", statistics.stdev(times))

    timer = timeit.Timer('thing == thing2', 'from nti.schema.tests.test_eqhash import ManyThing as Thing; thing=Thing(); thing2 = Thing()')
    times = timer.repeat()
    print("Avg many  eq", statistics.mean(times), "stddev", statistics.stdev(times))


# Before
#
# Avg Base  eq 0.790581703186 stddev 0.00709198228224
# Avg Child eq 1.44241364797 stddev 0.00058100921717
# Avg Super  eq 0.772551695506 stddev 0.0120497874892
# Avg Super2  eq 0.230642795563 stddev 0.00981929676758

# Best attrgetter, params as keywords:
# Avg Base  eq 0.57781457901 stddev 0.00472933000447
# Avg Child eq 1.13719065984 stddev 0.00751860996924
# Avg Super  eq 0.576888004939 stddev 0.0073053209526
# Avg Super2  eq 0.221588929494 stddev 0.00154292380992

# Code generation
# Avg Base  eq 0.436311562856 stddev 0.0159609115497
# Avg Child eq 0.93773595492 stddev 0.0244992238919
# Avg Super  eq 0.443862199783 stddev 0.00816548353324
# Avg Super2  eq 0.216485659281 stddev 0.00651497010124

## Many attributes
# Before
# Avg Base  eq 0.762074232101 stddev 0.00893669830878
# Avg Child eq 1.46989099185 stddev 0.0260021505811
# Avg Super  eq 0.776515642802 stddev 0.011819047442
# Avg Super2  eq 0.2257057031 stddev 0.0025750486944
# Avg many  eq 1.56614136696 stddev 0.0195022584734

# Code generation
# Avg Base  eq 0.410983006159 stddev 0.00708241719015
# Avg Child eq 0.903119166692 stddev 0.0051626944104
# Avg Super  eq 0.41703470548 stddev 0.00604558003878
# Avg Super2  eq 0.208957354228 stddev 0.00508863378261
# Avg many  eq 0.797417243322 stddev 0.0198358058579

if __name__ == '__main__':
    import sys
    if '--timehash' in sys.argv:
        bench_hash()
    elif '--timeeq' in sys.argv:
        bench_eq()
    else:
        unittest.main()
