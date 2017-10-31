from django.core.cache import cache

from django_redis import get_redis_connection

from django.conf import settings

from base_cache import BaseCache

import json

class APICache(BaseCache):
    '''This APICache is used only to cache queries generated from the model_api section.
    It can be used for any other location, but it is designed to function well only with the model_api!!
    '''
    # the mental model here is 2 dictionaries.
    # the first dictionary: 
    # each model_type get's its own dictionary.  they are labeled by the model_name.
    # so we will have one for "profile" one for "token" etc.
    # redis allows us to get both of them at the same time...
    # say we are looking up a profile:
    # we get the "PROFILE" dictionary, and ask for the response to token
    #    key_set = PROFILE_DICT.get(token, None)
    #
    # key_set itself is a dictionary
    # for the given key_set
    #     response = KEY_SET.get(url)
    
    def __init__(self, model_name, token, url):
        super(APICache, self).__init__()
        
        self.model_name = model_name
        self.token = token
        self.url = url
        
        self.modified_model_name = 'api' + self.model_name


    def _get(self):
        
        response = None
        model_token_key = self.redis_connection.hget(self.modified_model_name, self.token) # this should hould the keyname, to a list!
        # it could also be None:
        
        if model_token_key is not None:
            # check that the url is in there....
            response = self.redis_connection.hget(model_token_key, self.url)
        
        if response is not None:
            response = json.loads(response)

        
        return response
    
    
    def _set(self, value):

        if self.redis_connection.hget(self.modified_model_name, self.token) == None:
            self.redis_connection.hset(self.modified_model_name, self.token, self.generate_key_name())
        # we expect that token+model_name is also a set...
        
        
        value = json.dumps(value)
        response = self.redis_connection.hset(self.generate_key_name(), self.url, value)
        
        return response
    
    def _clear(self, token = None, *args, **kwargs):
        

        if token is not None: # this is level 1
            self.redis_connection.delete(self.generate_key_name())
            self.redis_connection.hdel(self.modified_model_name, token)
            
        else:
            self.redis_connection.delete(self.modified_model_name)


    def _clear_level(self, level, token = None, *args, **kwargs):
        if level == 0:
            return
        elif level == 1:
            self.clear(token = token)
        elif level == 2:
            self.clear(token = None)
    

    def clear_all(self):
        self.redis_connection.flushall()

    def generate_key_name(self):

        return self.modified_model_name + str(self.token)
