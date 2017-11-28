from django_framework.django_helpers.worker_helpers.job_widgets import BaseProcessResponse


class ProcessResponse(BaseProcessResponse):
    '''Determines what is put into the payload of a job. 
    We can use the model itself.  It is possible that different types of runnin gthis could necessitate different information in the future
    and we can add in a non-required job_model'''
    
    def run(self):
        
        worker_response_payload = self.worker_response.response_payload
        
        # we expect it to have 3 things...
        response = {}
        response['status'] = worker_response_payload['status']
        response['random_message'] = worker_response_payload['random_message']
        response['passthrough']    = worker_response_payload['passthrough']
        
        response['process_response_message'] = 'worker_response_message_here!'

        self.response = response
        
    def get_response(self):
        return self.response