
from base_variable import BaseVariable

class KafkaConfiguration(BaseVariable):
    
    @property
    def KAFKA_SERVER(self):
        var_name = 'kafka_server'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_kafka_server(self):
        return self._KAFKA_SERVER, None, None
    
    def _check_kafka_server(self, value):
        
        if value != None:
            self.assert_type(value, dict)
        return True


    @property
    def KAFKA_ENABLED(self):
        var_name = 'kafka_enabled'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_kafka_enabled(self):
        value = self.KAFKA_SERVER != None
        return value, None, None
    
    def _check_kafka_enabled(self, value):
        '''The value of the IV can be None, we will then generate a new IV per encryption'''
        
        self.assert_boolean(value = value)
        
        return True
