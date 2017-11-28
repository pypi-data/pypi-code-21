
from base_variable import BaseVariable

class ProjectName(BaseVariable):
    
    @property
    def PROJECT_NAME(self):
        var_name = 'project_name'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_project_name(self):
        return self._PROJECT_NAME, None, None
    
    def _check_project_name(self, value):

        self.assert_not_blank(value = value)

        return True
    