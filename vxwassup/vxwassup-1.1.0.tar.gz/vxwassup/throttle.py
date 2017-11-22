from functools import wraps

from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred, Deferred, inlineCallbacks
from twisted.internet.task import LoopingCall

from twisted.python import log


class Throttle(object):

    def __init__(self, manager, func, tps_limit, clock=None):
        self.manager = manager
        self.func = func
        self.instance = None
        self.tps_counter = 0
        self.tps_limit = tps_limit
        self.lc = LoopingCall(self.reset)
        self.clock = self.lc.clock = clock or reactor

    def start(self):
        # we have a transactions per second limit
        # so reset the counters every second
        if not self.lc.running:
            self.lc.start(1)

    def reset(self):
        self.tps_counter = 0
        if self.instance:
            return self.manager.resubmit_stashed(
                self.instance, self, self.func)

    def increment(self):
        self.tps_counter += 1

    def needs_throttling(self):
        return self.tps_counter >= self.tps_limit

    def wait_for_unthrottle(self):
        d = Deferred()

        def cb():
            if self.needs_throttling():
                self.clock.callLater(0, cb)
                return
            d.callback(True)

        cb()

        return d

    def manual(self, instance, *args, **kwargs):
        self.tps_counter = self.tps_limit
        return self.manager.stash(instance, self.func, args, kwargs)

    def stop(self):
        if self.lc.running:
            self.lc.stop()


class ThrottleManager(object):

    def __init__(self, clock=None):
        self.clock = clock or reactor
        self.throttles = []

    def __call__(self, tps_limit):
        return self.new(tps_limit)

    def new(self, tps_limit):
        def decorator(func):
            throttle = Throttle(self, func, tps_limit, self.clock)
            self.throttles.append(throttle)
            func.throttle = throttle

            @wraps(func)
            def wrapper(transport, *args, **kwargs):
                throttle.instance = transport
                if throttle.needs_throttling():
                    d = maybeDeferred(
                        self.stash, transport, func, args, kwargs)
                    d.addCallback(
                        lambda _: self.start_throttling(transport))
                    d.addCallback(
                        lambda _: throttle.wait_for_unthrottle())
                    d.addCallback(self.stop_throttling, transport)
                    d.addCallback(
                        lambda _: self.resubmit_stashed(
                            transport, throttle, func))
                    d.addErrback(log.err)
                    return d
                else:
                    throttle.increment()
                    return maybeDeferred(
                        func, transport, throttle, *args, **kwargs)
            wrapper.undecorated = func
            return wrapper
        return decorator

    def start(self):
        return [throttler.start() for throttler in self.throttles]

    def stop(self):
        return [throttler.stop() for throttler in self.throttles]

    def stash(self, instance, func, args, kwargs):
        return instance.stash(func, args, kwargs)

    @inlineCallbacks
    def resubmit_stashed(self, instance, throttle, func):
        stashed = yield maybeDeferred(instance.get_stashed, func)
        for (arg, kwarg) in stashed:
            yield func(instance, throttle, *arg, **kwarg)

    def start_throttling(self, instance):
        return instance.start_throttling()

    def stop_throttling(self, result, instance):
        return instance.stop_throttling()
