from .models import Cache
from functools import wraps


def lrucache(key_str):
    def _lru_cache(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = key_str.format(*args, **kwargs)
            type = '{}.{}'.format(func.__module__, func.__name__)

            try:
                return Cache.objects.get(
                    key=key,
                    type=type
                ).results
            except Cache.DoesNotExist:
                result = func(*args, **kwargs)

                Cache.objects.create(
                    key=key,
                    type=type,
                    results=result
                )
                return result

        return wrapper

    return _lru_cache
