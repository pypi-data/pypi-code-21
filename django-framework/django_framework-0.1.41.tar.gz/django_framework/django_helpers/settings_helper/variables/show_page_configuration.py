
from base_variable import BaseVariable

class ShowPageConfiguration(BaseVariable):
    
    @property
    def DEFAULT_SHOW_NUMBER(self):
        var_name = 'default_show_number'
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_default_show_number(self):
        if hasattr(self, '_DEFAULT_SHOW_NUMBER'):
            value = self._DEFAULT_SHOW_NUMBER
        else:
            print('_DEFAULT_SHOW_NUMBER was not found and set to default of 25')
            value = 25
        
        return value, None, None
    
    def _check_default_show_number(self, value):
        self.assert_type(value = value, expected_type = int)
        return True
