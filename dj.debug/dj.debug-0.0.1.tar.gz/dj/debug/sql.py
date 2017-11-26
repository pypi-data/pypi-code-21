# -*- coding: utf-8 -*-

from contextlib import contextmanager

from .log import log_new_queries


@contextmanager
def debug_sql(debug_logger=None):
    from django.conf import settings
    from django.db import connection

    debug = settings.DEBUG
    settings.DEBUG = True
    queries = len(connection.queries)
    try:
        yield
    finally:
        log_new_queries(
            queries,
            debug_logger)
        settings.DEBUG = debug
