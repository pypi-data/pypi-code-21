import json
from .log import logger
from yaz.decorator import decorator
import functools

__all__ = ["cache"]


def _get_key(*args, **kwargs):
    return (args, kwargs)


@decorator
def cache(func, key=_get_key):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key_string = json.dumps(key(*args, **kwargs), sort_keys=True)

        if key_string in _cache:
            logger.debug("Cache hit for %s with key %s", func, key_string)
        else:
            logger.debug("Cache miss for %s with key %s", func, key_string)
            _cache[key_string] = func(*args, **kwargs)

        return _cache[key_string]

    _cache = {}
    return wrapper
