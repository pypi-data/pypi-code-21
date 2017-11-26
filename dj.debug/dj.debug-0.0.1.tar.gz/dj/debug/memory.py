
import gc
import resource
from contextlib import contextmanager


def _get_mem_usage(proc=None):
    return resource.getrusage(
        proc or resource.RUSAGE_SELF).ru_maxrss


@contextmanager
def memusage(proc=None):
    usage = {}
    gc.collect()
    usage["initial"] = _get_mem_usage(proc)
    yield usage
    gc.collect()
    usage["after"] = _get_mem_usage(proc)
    usage["used"] = usage["after"] - usage["initial"]
