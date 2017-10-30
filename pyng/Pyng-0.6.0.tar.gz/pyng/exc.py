#!/usr/bin/python
"""\
@file   exc.py
@author Nat Goodspeed
@date   2011-01-04
@brief  Utilities for manipulating Python exceptions

Copyright (c) 2011, Nat Goodspeed
"""

import sys
import functools
import itertools

class reraise(object):
    """
    Consider this cleanup pattern:

    try:
        some_code()
    except Exception:
        essential_cleanup()
        raise

    You want to perform the cleanup on exception, but nonetheless you want to
    propagate the original exception out to the caller, original traceback and
    all.

    Sadly, because of Python's global current exception, that works only if
    essential_cleanup() does not itself handle any exceptions. For instance:

    try:
        x = some_dict[some_key]
    except KeyError:
        print "No key %r" % some_key

    This innocuous code is enough to foul up the no-args 'raise' statement in
    the 'except' clause that calls essential_cleanup().

    You can capture sys.exc_info() and re-raise specifically that exception:

    try:
        some_code()
    except Exception:
        type, value, tb = sys.exc_info()
        essential_cleanup()
        raise type, value, tb

    But now you've constructed the kind of reference loop against which
    http://docs.python.org/release/2.5.4/lib/module-sys.html#l2h-5141
    specifically warns, storing a traceback into a local variable.

    This is better:

    try:
        some_code()
    except Exception:
        type, value, tb = sys.exc_info()
        try:
            essential_cleanup()
            raise type, value, tb
        finally:
            del tb

    but you must admit it's pretty verbose -- it almost completely obscures
    the nature of the cleanup. Plus it's a PITB to remember.

    reraise encapsulates that last pattern, permitting you to write:

    try:
        some_code()
    except Exception:
        with reraise():
            essential_cleanup()

    This is as terse as the original, guarantees to preserve the original
    exception and avoids reference loops.

    As in the original construct, if essential_cleanup() itself raises an
    exception, that exception propagates out to the caller instead of the one
    raised by some_code().
    """
    def __enter__(self):
        self.type, self.value, self.tb = sys.exc_info()
        return self

    def __exit__(self, type, value, tb):
        try:
            if type or value or tb:
                # If code in the 'with' block raised an exception, just let that
                # exception propagate.
                return False

            if not (self.type or self.value or self.tb):
                # If there wasn't a current exception at __enter__() time,
                # don't raise one now.
                return False

            # This 'with' statement was entered with a current exception, and
            # code in the block did not override it with a newer exception.
            # Re-raise the one we captured in __enter__().
            raise self.type, self.value, self.tb

        finally:
            # No matter how we leave this method, always delete the traceback
            # member.
            del self.tb

def retry_func(func, *args, **kwds):
    """
    Call the passed callable 'func' with *args, **kwds. Return whatever it
    successfully returns. But on certain exceptions, retry the call.

    keyword-only args:
    exc=Exception
    times=3
    when=lambda e: True
    between=lambda tries: None

    If func(*args, **kwds) raises an exception of class 'exc', and if
    bool('when'(exception)) is True, retry the call up to 'times'. 'times' is
    the maximum number of times retry_func() will attempt to call 'func': a
    first "try" followed by up to ('times'-1) "retries".

    If a retry is necessary, retry_func() will call your 'between' callable,
    passing an int indicating how many tries it has attempted so far: 1, 2, ...
    This may be used to log the exception (via sys.exc_info()) and the fact
    that the operation is being retried. 'between' is not called after 'times'
    exceptions. That is, 'between' will be called at most ('times'-1) times.
    It is called when retry_func() is about to retry the original call, but
    not when retry_func() is giving up and letting the exception propagate.

    As in the case of try...except (exA, exB), 'exc' can be a tuple of
    exception classes.

    The filter callable 'when' can be used to select (e.g.) OSError
    exceptions with particular errno values.

    Example:

    retry_func(os.remove, somefilename,
               exc=OSError, when=lamba e: e.errno == errno.EACCES)

    If func(*args, **kwds) raises an exception that doesn't match 'exc', or if
    bool('when'(exception)) is False, or if retry_func() has already called
    'func' 'times' times, the exception will propagate to the caller.

    retry_func() does not examine the value returned by 'func'. If you want to
    retry somefunc(somearg) until you see a particular return value, define a
    distinctive Exception subclass. Then define a function that will call your
    target 'func' and raise your distinctive Exception subclass if the return
    value isn't what you want. Then pass that wrapper function and your
    distinctive Exception subclass to retry_func().

    Example:

    class NoneBad(Exception):
        pass

    def noNone(func, *args, **kwds):
        ret = func(*args, **kwds)
        if ret is None:
            raise NoneBad()
        return ret

    value = retry_func(noNone, somefunc, somearg, exc=NoneBad)
    # value will not be None. If calling somefunc(somearg) 'times' times
    # continues to produce None, this call will raise NoneBad instead.
    """
    exc     = kwds.pop("exc", Exception)
    times   = kwds.pop("times", 3)
    when    = kwds.pop("when", lambda e: True)
    between = kwds.pop("between", lambda tries: None)

    for tries in itertools.count(1):
        try:
            return func(*args, **kwds)
        except exc, e:
            # Here we know the exception matches 'exc'.
            if not when(e):
                # Doesn't match caller's 'when' condition
                raise
            if tries >= times:
                # func() failed too many times, give up
                raise
            # We're about to retry. Call 'between'.
            between(tries)

class retry(object):
    """
    decorator version of retry_func()

    Example:

    @retry(exc=OSError, when=lamba e: e.errno == errno.EACCES,
           between=lambda tries: time.sleep(1))
    def my_remove(path):
        os.remove(path)
    """
    def __init__(self, exc=Exception, times=3, when=lambda e: True, between=lambda tries: None):
        self.exc     = exc
        self.times   = times
        self.when    = when
        self.between = between

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            return retry_func(func,
                              exc=self.exc, times=self.times,
                              when=self.when, between=self.between,
                              *args, **kwds)
        return wrapper
