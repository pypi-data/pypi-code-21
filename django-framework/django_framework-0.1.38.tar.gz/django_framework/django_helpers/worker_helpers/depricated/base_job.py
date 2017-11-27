import arrow
import json
import copy
import requests
from django.db.models import Model

from django_framework.django_helpers.manager_helpers import get_manager
from django_framework.django_helpers.serializer_helpers import get_serializer

class BaseWorkerJob(object):
    ALLOWED_JOB_TYPES = ['asynchronous', 'synchronous', 'local']
    def __init__(self, 
                 command, action,
                 allowed_job_types, 
                 allowed_priorities, 
                 timeout_ttl,
                 default_job_type = None,
                 default_priority = None
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
    
    def create_initial_payload(self, model, *args, **kwargs):
        # we expect the person calling to give us a model of who they are!
        # this is going to be django compatible
        raise NotImplemented('Please implement me!')
    
    def process_response(self, model, job_model, response = None, *args, **kwargs):
        # this is not going to be django compatible.
        if response is not None:
            self.process_response_class()
        
        raise NotImplemented('Please Impement me!')
    
    def generate_response(self, *args, **kwargs):
        raise NotImplemented('Please Implement me,  please return with a dict!')
        

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
                
                
        