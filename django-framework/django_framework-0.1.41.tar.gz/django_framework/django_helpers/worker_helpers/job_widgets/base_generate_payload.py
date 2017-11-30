
class BaseGeneratePayload(object):
    '''Determines what is put into the payload of a job. 
    We can use the model itself.  It is possible that different types of runnin gthis could necessitate different information in the future
    and we can add in a non-required job_model'''
    def __init__(self, model, job_model = None, *args, **kwargs):
        
        
        
        self.args = args
        self.kwargs = kwargs
        
        self.model = model
        self.job_model = job_model
        
        if self.model == None:
            raise ValueError('You cannot create this update status job initial payload!')

        
        run = self.kwargs.get('run', True)
        
        if run:
            self.run()

    def run(self):
        
        raise NotImplemented('Please implement a run!')
    
    
    def get_response(self):
        raise NotImplemented('we exepct a jsonable thing, usually a dictionary.')
    