
from base_variable import BaseVariable

class DatabaseConfiguration(BaseVariable):
    
    @property
    def DATABASE_SERVER(self):
        var_name = 'database_server'
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_database_server(self):
        return self._DATABASE_SERVER, None, None
    
    def _check_database_server(self, value):
        self.assert_type(value = value, expected_type = dict)
        return True
