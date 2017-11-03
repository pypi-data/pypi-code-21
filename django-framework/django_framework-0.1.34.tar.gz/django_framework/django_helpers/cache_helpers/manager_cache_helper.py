from django.core.cache import cache

from django_redis import get_redis_connection

import json
from django.conf import settings

from base_cache import BaseCache

class ManagerCache(BaseCache):
    '''This APICache is used only to cache queries generated from the model_api section.
    It can be used for any other location, but it is designed to function well only with the model_api!!
    '''

    def __init__(self, model_name, key):
        super(ManagerCache, self).__init__()
        
        self.model_name = model_name
        
        self.key = key
        self.key = self.generate_key_name()
        self._redis_connection = None
        
        
    def _get(self):
        response = self.redis_connection.get(self.key) # simple key value lookup
        # it could also be None:
        if response is not None:
            response = json.loads(response)

        return response
    
    
    def _set(self, value, ttl = None):

        # we first check that the model_name has this use
        # set the expire time in ttl in seconds
        value = json.dumps(value)
        
        if ttl is None:
            #If not specified, then ttl is forever
            response = self.redis_connection.set(self.key, value)
            
        else:
            # ttl in seconds
            response = self.redis_connection.setex(name = self.key, value = value, time = ttl)
        
        return response
    
    def _clear(self):
        response = self.redis_connection.delete(self.key)
        return response
    
    def generate_key_name(self):
        return 'manager:' + self.model_name + ':' +self.key
    
    
    
