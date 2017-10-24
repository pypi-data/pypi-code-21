# -*- coding: utf-8 -*-
###############################################################################
#   Copyright 2006 to the present, Orbitz Worldwide, LLC.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
###############################################################################
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from twisted.internet import defer
from twisted.internet import threads


def deferredAsThread(func):
    """This decorator wraps functions and returns deferred
       See twisted.internet.threads.deferToThread
       you should only use this decorator if there are no
       side effects .. ie you are only emitting data, not
       modifying class or server state inside of the thread.
       @return (defer.Deferred)
    """

    def newfunc(*args, **kwargs):
        return threads.deferToThread(func, *args, **kwargs)

    return newfunc


def deferredInThreadPool(pool=None, R=None):
    """This decorator will place a method into a threadpool.
       If you don't provide a pool, a default will be guessed.
       See twisted.internet.threads.deferToThreadPool
       you should only use this decorator if there are no
       side effects .. ie you are only emitting data, not
       modifying class or server state inside of the thread.
       @param R (reactor)
       @return (defer.Deferred)
    """
    if not R:
        from twisted.internet import reactor
        R = reactor
    if not pool:  # provide a default thread pool
        pool = R.getThreadPool()

    def decorator(func):
        def newfunc(*a, **kw):
            """I call blocking python code in a seperate thread.
               I return a deferred and will fire callbacks or errbacks.
            """
            return threads.deferToThreadPool(R, pool, func, *a, **kw)

        return newfunc

    return decorator


def synchronizedInThread(R=None):
    """This decorator will make a blocking call from a thread to
       the reactor and wait for all callbacks.  the result will
       be from the callback chain. Effectively useless unless
       you are in a seperate thread.
       #only good use case for this is in the decorators below
       ``threadedSafeDeferred`` and ``threadedSafePoolDeferred``
        ... use of this decorator is discouraged unless you
       know what it does.
       @param R (reactor)
       @raise any exception
       @return (object)
    """
    if not R:
        from twisted.internet import reactor
        R = reactor

    def decorator(func):
        def newfunc(*a, **kw):
            # works with deferred and blocking methods
            return threads.blockingCallFromThread(R, func, *a, **kw)

        return newfunc

    return decorator


def threadSafeDeferred(R=None):
    """This decorator will run a method in a seperate thread and
       wait for all callbacks/errbacks to fire before firing its
       own callbacks/errbacks.
       you should only use this decorator if there ARE
       side effects .. ie you are modifying class or server state
       inside of the thread.
       @param R (reactor)
       @return (defer.Deferred)
    """
    if not R:
        from twisted.internet import reactor
        R = reactor

    def decorator(func):
        def newfunc(*a, **kw):
            return func(*a, **kw)

        # decorate newfunc in a blocking reactor call
        return synchronizedInThread(R)(newfunc)

    # decorate decorator in a thread
    return deferredAsThread(decorator)


def threadSafePoolDeferred(pool=None, R=None):
    """This decorator will run a method in a thread pool and
       wait for all callbacks/errbacks to fire before firing its
       own callbacks/errbacks.  If you don't provide a thread
       pool, then a default will be selected for you.
       you should only use this decorator if there ARE
       side effects .. ie you are modifying class or server state
       inside of the thread.
       @param pool (thread pool object)
       @param R (reactor)
       @return (defer.Deferred)
    """
    if not R:
        from twisted.internet import reactor
        R = reactor
    if not pool:  # pick a thread pool
        pool = R.getThreadPool()

    def decorator(func):
        def newfunc(*a, **kw):
            return func(*a, **kw)

        # decorate newfunc in a blocking reactor call
        return synchronizedInThread(R)(newfunc)

    # decorate decorator in a thread pool
    return deferredInThreadPool(pool, R)(decorator)


def synchronizedDeferred(lock):
    """The function will run with the given lock acquired"""
    # make sure we are given an acquirable/releasable object
    assert isinstance(lock, (defer.DeferredLock, defer.DeferredSemaphore))

    def decorator(func):
        """Takes a function that will aquire a lock, execute the function,
           and release the lock.  Control will then be returned to the
           reactor for err/callbacks to run.

           returns deferred
        """

        def newfunc(*args, **kwargs):
            return lock.run(func, *args, **kwargs)

        return newfunc

    return decorator


_EXPORTS = [
    'deferredAsThread',
    'deferredInThreadPool',
    'synchronizedInThread',
    'threadSafeDeferred',
    'threadSafePoolDeferred',
    'synchronizedDeferred',
]

# export our methods
__all__ = _EXPORTS
