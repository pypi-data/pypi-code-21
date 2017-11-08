""" Caching module
"""
try:
    from eea.cache import event
    from eea.cache import cache as eeacache
    # pyflakes
    flush = event.flush
    flushRelatedItems = event.flushRelatedItems
    flushBackRefs = event.flushBackRefs
    ramcache = eeacache
except ImportError:
    # Fail quiet if required cache packages are not installed in order to use
    # this package without caching
    from eea.sparql.cache.nocache import ramcache
    from eea.sparql.cache.nocache import flush, flushBackRefs, flushRelatedItems

from eea.sparql.cache.cache import cacheSparqlKey, cacheSparqlMethodKey

__all__ = [
    ramcache.__name__,
    cacheSparqlKey.__name__,
    cacheSparqlMethodKey.__name__,
    flush.__name__,
    flushBackRefs.__name__,
    flushRelatedItems.__name__,
]
