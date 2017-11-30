
from base_variable import BaseVariable

class DebugConfiguration(BaseVariable):
    
    @property
    def DEBUG(self):
        var_name = 'debug'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_debug(self):
        return self._DEBUG, None, None
    
    def _check_debug(self, value):

        self.assert_boolean(value = value)

        return True
    
    ###################
    
    @property
    def SHOW_DEBUG_ERROR(self):
        var_name = 'show_debug_error'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_show_debug_error(self):
        return self._SHOW_DEBUG_ERROR, None, None
    
    def _check_show_debug_error(self, value):

        self.assert_boolean(value = value)

        return True
    
    #####
    
    @property
    def SHOW_DEBUG_TRACEBACK(self):
        var_name = 'show_debug_traceback'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_show_debug_traceback(self):
        return self._SHOW_DEBUG_TRACEBACK, None, None
    
    def _check_show_debug_traceback(self, value):

        self.assert_boolean(value = value)

        return True