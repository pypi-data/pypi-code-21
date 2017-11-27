import arrow
import json
import copy
import requests
from django.db.models import Model

from django_framework.django_helpers.manager_helpers import get_manager
from django_framework.django_helpers.serializer_helpers import get_serializer

from base_worker_response import BaseWorkerResponse



class BaseWorkerJob(object):
    '''This class holds the requirement for what a "job" is. '''
    ALLOWED_JOB_TYPES = ['asynchronous', 'synchronous', 'local']
    def __init__(self, 
                 command, action,
                 allowed_job_types, 
                 allowed_priorities, 
                 timeout_ttl,
                 default_job_type = None,
                 default_priority = None,
                 
                 
                 initial_payload_class = None,
                 response_generator_class = None,
                 process_response_class  = None,
                 ):
        
        self.allowed_job_types = allowed_job_types  # the allowed job types for this job
        self.allowed_priorities = allowed_priorities # a list of specified priorities, typically defaulted
        self.command = command # job command name
        self.action  = action # job action name
        self.timeout_ttl = timeout_ttl # number of seconds for the job to be waiting before it is considered timeout from start.
                                       # note that it is added to the run_at if it is not none
    
        self.default_job_type = default_job_type
        
        if self.default_job_type is None:
            self.default_job_type = self.allowed_job_types[0]
        
    
        self.generate_initial_payload_class = initial_payload_class
        if self.generate_initial_payload_class is None:
            raise ValueError('Please provide a class/function to handle how to generate an initial payload!')
    
        self.response_generator_class = response_generator_class
        if self.response_generator_class is None:
            raise ValueError('Please provide a class/function to handle how to generate a response!')
    
        self.process_response_class = process_response_class
        if self.process_response_class is None:
            raise ValueError('Please provide a class/function to handle how to process a response!')
    
    
    
    
    def validate_and_clean_job_request(self, **kwargs):
        
        if kwargs.get('command') != self.command:
            raise ValueError('This command does not match!')
        if kwargs.get('action') != self.action:
            raise ValueError('This action does not match!')
        
        job_type = kwargs.get('job_type')
        if job_type is not None:
            if job_type not in self.allowed_job_types:
                raise ValueError('The Job type specified is NOT ALLOWED or not recognized.')
            
        else:
            job_type = self.default_job_type
            
            
        run_at = arrow.get(kwargs.get('run_at', None))
        timeout = kwargs.get('timeout', self.timeout_ttl)
        try:
            int(timeout)
        except:
            raise ValueError('The job timeout must be an integer.')
        

        params = {}
        params['command'] = kwargs.get('command')
        params['action'] = kwargs.get('action')
        params['job_type'] = job_type # specified in logic above
        params['run_at'] = run_at
        params['timeout_at'] = run_at.replace(seconds=+ timeout)
        params['timeout'] = timeout
        
        return params
    
    def generate_initial_payload(self, model, model_name, **kwargs):
        aninstance = self.generate_initial_payload_class(model_name = model_name, model = model, run = True, **kwargs)
        return aninstance.get_response()
    
    def process_response(self, model, job_model, worker_response, *args, **kwargs):
        instance = self.process_response_class(model = model, job_model = job_model, worker_response = worker_response, *args, **kwargs)
        return instance.get_response()
    
    def generate_response(self, model, job_model, response,*args, **kwargs):
        
        if response is None:
            initial_payload = job_model.initial_payload 
            
            instance = self.response_generator_class(response = response, initial_payload = initial_payload, *args, **kwargs)
            response = instance.get_response()
            response = BaseWorkerResponse(status = 3, response_payload = response, command = job_model.command, action = job_model.action, initial_payload = job_model.initial_payload, job_model = job_model, response_at = None)
            
        else:
            response = BaseWorkerResponse(status = response.get('status'), response_payload = response, response_at = None)
#             response = BaseWorkerResponse(status = 3, response_payload = {'status' : 0, 'status_alt' : 'synchronous/local job pass through!'}, command = job_model.command, action = job_model.action, initial_payload = job_model.initial_payload, job_model = job_model, response_at = None)

        worker_response = response
        return worker_response
    
import collections
class BaseWorkerJobRegistry(object):
    
    def __init__(self):
        self.allowed_jobs = collections.defaultdict(dict)
        
    
    def add_job(self, job):
        
        if type(job) != BaseWorkerJob:
            raise ValueError('Currently you must add a job of the BaseWorkerJob type!')
        
        
        self.allowed_jobs[job.command][job.action] = job
        
        
    def find_job(self, command, action):
        try:
            return self.allowed_jobs[command][action]
        except:
            raise ValueError('The command/action combination was not found as a registered job for this model')
    
    
    def list_jobs(self):
        for command, actions in self.allowed_jobs.items():
            for action, job in actions.items():
                print(command, action, job)
                
    
    def get_allowed_jobs_doc(self):
        
        response = []
        for command, actions in self.allowed_jobs.items():
            
            for action, job in actions.items():
                adict = {}
                adict['command'] = command
                adict['action'] = action
                adict['description'] = None
                response.append(adict)
                
                
        return response
            
                
                
                
        
        
        