
from base_variable import BaseVariable

class RedisConfiguration(BaseVariable):
    
    @property
    def REDIS_SERVER(self):
        var_name = 'redis_server'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_redis_server(self):
        return self._REDIS_SERVER, None, None
    
    def _check_redis_server(self, value):
        
        if value != None:
            self.assert_type(value, dict)
            
        # we can further check type etc but we can deal with that later

        return True


    @property
    def REDIS_ENABLED(self):
        var_name = 'redis_enabled'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_redis_enabled(self):
        value = self.REDIS_SERVER != None
        return value, None, None
    
    def _check_redis_enabled(self, value):
        '''The value of the IV can be None, we will then generate a new IV per encryption'''
        
        self.assert_boolean(value = value)
        
        return True
