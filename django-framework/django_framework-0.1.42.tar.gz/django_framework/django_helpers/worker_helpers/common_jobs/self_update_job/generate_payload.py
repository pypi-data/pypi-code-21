from django_framework.django_helpers.worker_helpers.job_widgets import BaseGeneratePayload


class GeneratePayload(BaseGeneratePayload):
    '''Determines what is put into the payload of a job. 
    We can use the model itself.  It is possible that different types of runnin gthis could necessitate different information in the future
    and we can add in a non-required job_model'''
    
    def run(self):
        
        self.response = {}
        self.response['message'] = 'This is a test job!'
        
    
    def get_response(self):
        
        return self.response
