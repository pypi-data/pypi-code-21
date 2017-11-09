
import json

class BaseProcessResponse(object):
    '''a Django model that actually writes the responses to various rows in the DB'''
    def __init__(self, model, job_model, worker_response, *args, **kwargs):
        
        self.args = args
        self.kwargs = kwargs
        
        self.model = model
        self.job_model =  job_model
        self.worker_response = worker_response
        
        
        self.response = None
        
        if self.kwargs.get('run', True):
            self.run()

    def run(self):
        raise NotImplemented()

    def get_response(self):
        raise NotImplemented()
    
    def set_response_payload(self, response):
        '''This only needs to be set if we wish to update the response_payload in the actual job model, this will overwrite.'''
        if self.response is None:
            self.response = {}
            
        self.response['response_payload'] = json.dumps(response)