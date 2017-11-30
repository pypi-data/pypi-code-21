
from base_variable import BaseVariable

class SecretKey(BaseVariable):
    
    @property
    def SECRET_KEY(self):
        var_name = 'secret_key'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_secret_key(self):
        return self._SECRET_KEY, None, None
    
    def _check_secret_key(self, value):
        self.assert_not_blank(value = value)

        return True
    