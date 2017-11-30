
from base_variable import BaseVariable

class TripleDESToken(BaseVariable):
    
    @property
    def TRIPLE_DES_TOKEN_KEY(self):
        var_name = 'triple_des_token_key'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_triple_des_token_key(self):
        return self._TRIPLE_DES_TOKEN_KEY, None, None
    
    def _check_triple_des_token_key(self, value):
        
        self.assert_not_blank(value = value)
        if len(value) > 20:
            raise ValueError('The TripleDES key should be long and secure (max 32 char).')
        return True


    @property
    def TRIPLE_DES_TOKEN_IV(self):
        var_name = 'triple_des_token_iv'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_triple_des_token_iv(self):
        return self._TRIPLE_DES_TOKEN_IV, None, None
    
    def _check_triple_des_token_iv(self, value):
        '''The value of the IV can be None, we will then generate a new IV per encryption'''
        
        if value == '':
            raise ValueError('The IV shouldnt be empty string, either None or something longer')
        
        
        return True
