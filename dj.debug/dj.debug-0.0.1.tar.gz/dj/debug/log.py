
import logging
import time


logger = logging.getLogger(__name__)


def log_timing(start, timed=None, debug_logger=None):
    debug_logger = debug_logger or logger
    timing = time.time() - start
    if timed:
        msg = (
            "Timing for %s: %s seconds"
            % (timed, timing))
    else:
        msg = (
            "Timing: %s seconds"
            % timing)
    debug_logger.debug(msg)


def log_new_queries(queries, debug_logger=None):
    from django.db import connection

    debug_logger = debug_logger or logger
    new_queries = list(connection.queries[queries:])
    for query in new_queries:
        debug_logger.debug(query["time"])
        debug_logger.debug("\t%s", query["sql"])
    debug_logger.debug("total db calls: %s", len(new_queries))
