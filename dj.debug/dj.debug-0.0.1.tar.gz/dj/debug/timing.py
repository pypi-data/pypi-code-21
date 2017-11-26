
import time
from contextlib import contextmanager


from .log import logger, log_timing


@contextmanager
def timings(timed=None, debug_logger=None):
    start = time.time()
    yield
    log_timing(
        start,
        timed,
        debug_logger or logger)
