
from base_variable import BaseVariable

class JobConfiguration(BaseVariable):
    
    @property
    def ALLOW_SEND_JOBS(self):
        var_name = 'allow_send_jobs'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_allow_send_jobs(self):
        return self._ALLOW_SEND_JOBS, None, None
    
    def _check_allow_send_jobs(self, value):
        self.assert_boolean(value = value)
        return True
    
    ##########

    @property
    def SEND_JOB_URL(self):
        var_name = 'send_job_url'
        
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_send_job_url(self):
        return self._SEND_JOB_URL, None, None
    
    def _check_send_job_url(self, value):
        
        if self.ALLOW_SEND_JOBS == True:
            self.assert_is_url(value = value)
            
        return True

    #########
    @property
    def JOB_REPLY_URL(self):
        var_name = 'job_reply_url'
        return self._get_set_variables(var_name = var_name)
    
    def _get_job_reply_url(self):
        return self._JOB_REPLY_URL, None, None
    
    def _check_job_reply_url(self, value):
        
        if self.ALLOW_SEND_JOBS == True:
            self.assert_is_url(value = value)
        return True
