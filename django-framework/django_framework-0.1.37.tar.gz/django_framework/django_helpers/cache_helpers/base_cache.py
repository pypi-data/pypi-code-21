from django.conf import settings
from functools import wraps


def try_except_cache(func):
    
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        if settings.REDIS_CACHE_ENABLED != True:
            return None
        
        try:
            return func(*args, **kwargs)
        except Exception, e:
            return None
#             return json_error
    return wrapper


from django_redis import get_redis_connection
class BaseCache(object):
    ''''''
    def __init__(self):
        self._redis_connection = None
        
    @property
    def redis_connection(self):
        if self._redis_connection == None:
            self._redis_connection = get_redis_connection('default')
        
        return self._redis_connection
    
    @try_except_cache
    def get(self):
        if settings.REDIS_CACHE_ENABLED != True:
            return None
        
        return self._get()

    
    @try_except_cache
    def set(self, *args, **kwargs):
        if settings.REDIS_CACHE_ENABLED != True:
            return None
        self._set(*args, **kwargs)
    
    @try_except_cache
    def clear(self, *args, **kwargs):
        if settings.REDIS_CACHE_ENABLED != True:
            return None
        
        self._clear(*args, **kwargs)
        
    @try_except_cache
    def clear_level(self, level = None, *args, **kwargs):

        if settings.REDIS_CACHE_ENABLED != True:
            return None
        
        self._clear_level(level, *args, **kwargs)
    

