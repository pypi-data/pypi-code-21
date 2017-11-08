# -*- coding: utf-8 -*-

"""
Recipe
~~~~~~~~~~~~~~~~~~~~~
"""
import logging

from recipe_caching.caching_query import CachingQuery

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logging.getLogger(__name__).addHandler(NullHandler())


def query_callable(regions, query_cls=CachingQuery):
    def query(*arg, **kw):
        return query_cls(regions, *arg, **kw)
    return query


__all__ = [query_callable]
