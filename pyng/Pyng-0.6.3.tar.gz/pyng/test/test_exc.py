#!/usr/bin/python
"""\
@file   test_exc.py
@author Nat Goodspeed
@date   2011-01-04
@brief  Test exc.py functionality

Copyright (c) 2011, Nat Goodspeed
"""

from __future__ import with_statement   # for Python 2.5

import sys
import unittest
import exc

class FooError(Exception):
    pass

class BarError(Exception):
    pass

def raiser(exc):
    raise exc

class TestReraise(unittest.TestCase):
    def setUp(self):
        pass

    def test_plain_raise(self):
        # Prove claim that no-args 'raise' can get confused
        try:                            # this is outer code
            try:
                raiser(FooError("foo"))
            except FooError, err:
                # This is cleanup code
                try:
                    x = int("7a")
                except ValueError:
                    # it's okay, we've handled it...
                    x = 7
                # except now we've reset the global exception info...
                raise
        except FooError, err:
            # This we do NOT expect, at least not in Python 2.x.
            self.assert_(False)
        except ValueError, err:
            self.assert_(True)
        else:
            # There better be an exception of SOME kind!
            self.assert_(False)

    def test_reraise(self):
        # reraise should handle this better
        try:                            # this is outer code
            try:
                raiser(FooError("foo"))
            except FooError, err:
                with exc.reraise():
                    # This is cleanup code
                    try:
                        x = int("7a")
                    except ValueError:
                        # it's okay, we've handled it...
                        x = 7
        except FooError, err:
            # This time we should get our original FooError
            self.assertEqual(str(err), "foo")
        except ValueError, err:
            self.assert_(False)
        else:
            self.assert_(False)

    def test_cleanup_exc(self):
        # reraise lets cleanup exception propagate out
        try:                            # this is outer code
            try:
                raiser(FooError("foo"))
            except FooError, err:
                with exc.reraise():
                    # This is cleanup code -- whoops, uncaught exception!
                    x = int("7a")
        except FooError, err:
            # reraise shouldn't discard cleanup exception
            self.assert_(False)
        except ValueError, err:
            self.assert_(True)
        else:
            self.assert_(False)

    def test_no_current_exc(self):
        # If there wasn't already a current exception, reraise doesn't
        # introduce one.
        try:                            # this is outer code
            with exc.reraise():
                pass
        except FooError, err:
            self.assert_(False)
        except ValueError, err:
            self.assert_(False)
        except TypeError, err:
            self.assert_(False)
        else:
            self.assert_(True)

class ErrorFunc(object):
    def __init__(self, exc, times=2):
        self.exc = exc
        self.times = times
        self.count = 0

    # You can pass an ErrorFunc object to retry_func()
    def __call__(self, value=None):
        self.count += 1
        if self.count <= self.times:
            raise self.exc
        return value

    betweens = set()

    # or you can just call retry_method, wrapped with @retry.
    # These particular parameters must be coordinated with
    # TestRetry.test_decorator().
    @exc.retry(exc=FooError, times=2, when=lambda e: str(e) == "true", between=betweens.add)
    def retry_method(self, value=None):
        return self(value)

class CatchExcInfo(object):
    def __init__(self):
        self.type = None
        self.value = None
        self.tries = None

    def __call__(self, tries):
        self.tries = tries
        self.type, self.value, _ = sys.exc_info()

def reject_bar(func, *args, **kwds):
    ret = func(*args, **kwds)
    if ret == "bar":
        raise BarError("got bar!")
    return ret

class TestRetry(unittest.TestCase):
    def setUp(self):
        pass

    def test_success(self):
        """no retries necessary"""
        func = ErrorFunc(FooError(), times=0)
        self.assertEqual(func("abc"), "abc")
        self.assertEqual(exc.retry_func(func, "abc"), "abc")

    def test_one(self):
        func = ErrorFunc(FooError(), times=1)
        self.assertEqual(exc.retry_func(func, "abc"), "abc")
        self.assertEqual(func.count, 2)

    def test_two(self):
        func = ErrorFunc(FooError(), times=2)
        self.assertEqual(exc.retry_func(func, "abc", exc=FooError, times=3), "abc")
        self.assertEqual(func.count, 3)

    def test_three(self):
        func = ErrorFunc(FooError(), times=3)
        try:
            exc.retry_func(func, "abc")
        except FooError:
            # After three tries, each of which raises FooError, retry_func()
            # should let the FooError propagate.
            self.assertEqual(func.count, 3)
        else:
            # We expect FooError.
            self.assert_(False)

    def test_when_true(self):
        func = ErrorFunc(FooError("true"), times=2)
        self.assertEqual(exc.retry_func(func, value="abc",
                                        exc=FooError, times=3,
                                        when=lambda e: str(e) == "true"),
                         "abc")

    def test_when_false(self):
        func = ErrorFunc(FooError("false"), times=2)
        try:
            exc.retry_func(func, "abc",
                           exc=FooError, times=3,
                           when=lambda e: str(e) == "true")
        except FooError:
            # The FIRST FooError should propagate, since it doesn't pass when().
            self.assertEqual(func.count, 1)
        else:
            self.assert_(False)

    def test_between(self):
        func = ErrorFunc(FooError(), times=3)
        betweens = set()
        try:
            exc.retry_func(func, value="abc",
                           exc=FooError, times=3, between=betweens.add)
        except FooError:
            self.assertEqual(func.count, 3)
            self.assertEqual(betweens, set((1, 2)))
        else:
            self.assert_(False)

    def test_between_exc_info(self):
        exception = FooError("distinct")
        func = ErrorFunc(exception, times=1)
        catcher = CatchExcInfo()
        self.assertEqual(exc.retry_func(func, "abc", exc=FooError, times=2, between=catcher),
                         "abc")
        self.assertEqual(catcher.type, FooError)
        self.assertEqual(str(catcher.value), "distinct")

    def test_exc_tuple_0(self):
        func = ErrorFunc(FooError(), times=1)
        self.assertEqual(exc.retry_func(func, "abc", exc=(FooError, BarError), times=2),
                         "abc")
        self.assertEqual(func.count, 2)

    def test_exc_tuple_1(self):
        func = ErrorFunc(BarError(), times=1)
        self.assertEqual(exc.retry_func(func, "abc", exc=(FooError, BarError), times=2),
                         "abc")
        self.assertEqual(func.count, 2)

    def test_ret_good(self):
        iterator = iter(("bar", "bar", "foo"))
        betweens = set()
        self.assertEqual(exc.retry_func(reject_bar, iterator.next,
                                        exc=BarError, times=3, between=betweens.add),
                         "foo")
        self.assertEqual(betweens, set((1, 2)))

    def test_ret_bad(self):
        iterator = iter(("bar", "bar", "bar"))
        betweens = set()
        try:
            exc.retry_func(reject_bar, iterator.next,
                           exc=BarError, times=3, between=betweens.add)
        except BarError:
            self.assertEqual(betweens, set((1, 2)))
        else:
            self.assert_(False)

    # We're not going to restate all the above for the retry decorator. Since
    # retry is implemented on retry_func(), we assume that if we can pass
    # through all the right parameters, and if the syntax works, we're good.
    # Also don't bother testing with a free function: if a decorator works
    # with a method, assume it also works with free functions.
    def test_decorator(self):
        func = ErrorFunc(FooError("true"), times=1)
        self.assertEqual(func.retry_method("abc"), "abc")
        self.assertEqual(func.count, 2)
        self.assertEqual(func.betweens, set((1,)))

if __name__ == "__main__":
    unittest.main()
