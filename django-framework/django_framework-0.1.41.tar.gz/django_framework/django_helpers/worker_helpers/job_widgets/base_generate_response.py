
import json
import requests


class BaseGenerateResponse(object):
    '''The BaseGenerateResponse is essentially a way to generate the proper Response we expect for this job.
    Because this logic is expected to also beused on 3rd party servers, it cannot use anything DJANGO related here.
    all relevant information for the proper generation of the response must be passed in or obtained within this class itself.
    '''
    def __init__(self, response, initial_payload, *args, **kwargs):
        '''
#             model is the model that is requesting the worker.  For instance Profile, 
#            job_model is the ProfileWorker and the associated Job row
           response is a string/json depending, that is the actual response
           intial_payload - the intial payload of a job.  enters as a string
        '''
        
#         model = self.model, job_model = job_model, response = response
        
        self.args = args
        self.kwargs = kwargs
        
        self.response = kwargs.get('response')
        self.initial_payload = self.convert_to_json(initial_payload) # always a string
        
        run = self.kwargs.get('run', True)
        if run:
            self.run()
        
    def run(self):
        raise NotImplemented('Implement a subclassed version of this method')
    
    def get_response(self):
        # typically returns a dictionary
        raise NotImplemented('Implement a subclassed version of this method')
    
    def convert_to_json(self, astr):
        return json.loads(astr)
