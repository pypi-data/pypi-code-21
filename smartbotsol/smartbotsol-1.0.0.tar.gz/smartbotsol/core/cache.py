from functools import wraps
from smartbotsol.singleton import Singleton

class Cache(object):
    """Cache interface"""

    __metaclass__ = Singleton

    STORE = None
    
    def get(self, parameter):
        raise NotImplementedError

    def add(self, key, value):
        raise NotImplementedError

    def to_dict(self):
        """Serializer"""
        raise NotImplementedError

    def from_dict(self, fdict):
        """Deserializer"""
        raise NotImplementedError

def _log(func):
    import logging
    log = logging.getLogger(__name__)
    @wraps(func)
    def wrap(*args, **kwargs):
        result = func(*args, **kwargs)
        log.debug('EXTRACT: {}'.format(result))
        return result
    return wrap
