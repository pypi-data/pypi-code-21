""" Caching module
"""
try:
    from eea.cache import cache as eeacache
    from eea.cache import event
    # pyflakes
    InvalidateCacheEvent = event.InvalidateCacheEvent
    ramcache = eeacache
    flush = event.flush
    flushBackRefs = event.flushBackRefs
    flushRelatedItems = event.flushRelatedItems
except ImportError:
    # Fail quiet if required cache packages are not installed in order to use
    # this package without caching
    from eea.epub.cache.nocache import ramcache
    from eea.epub.cache.nocache import InvalidateCacheEvent
    from eea.epub.cache.nocache import flush, flushBackRefs, flushRelatedItems

from eea.epub.cache.cache import cacheKey, updateBackRefs

__all__ = [
    ramcache.__name__,
    InvalidateCacheEvent.__name__,
    cacheKey.__name__,
    flush.__name__,
    flushBackRefs.__name__,
    flushRelatedItems.__name__,
    updateBackRefs.__name__,
]
