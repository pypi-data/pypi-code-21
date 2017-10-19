from functools import wraps

from twisted.internet.defer import maybeDeferred



def tap(f):
    """
    "Tap" a Deferred callback chain with a function whose return value is
    ignored.
    """
    @wraps(f)
    def _cb(res, *a, **kw):
        d = maybeDeferred(f, res, *a, **kw)
        d.addCallback(lambda ignored: res)
        return d
    return _cb
