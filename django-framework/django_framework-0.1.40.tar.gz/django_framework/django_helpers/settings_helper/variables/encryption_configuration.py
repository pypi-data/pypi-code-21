
from base_variable import BaseVariable

class EncryptionConfiguration(BaseVariable):
    
    @property
    def ENCRYPTION_SALT(self):
        var_name = 'encryption_salt'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_encryption_salt(self):
        return self._ENCRYPTION_SALT, None, None
    
    def _check_encryption_salt(self, value):
        
        if value != None and len(value) < 10:
            raise ValueError('The encryption salt should be long and secure (max 32 char).')
        return True

