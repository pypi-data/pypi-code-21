
import json
from base_cache import BaseCache


class NormalCache(BaseCache):

    def __init__(self, key):
        self._redis_connection = None
        self.key = key

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