import arrow
import json
import copy
import requests
from django.db.models import Model

from django_framework.django_helpers.manager_helpers import get_manager
from django_framework.django_helpers.serializer_helpers import get_serializer


class BaseWorker(object):
    # async jobs are sent to another server
    # sync jobs are processed IMMEDIATELY
    # local is processed on local server using management tools
    
    ALLOWED_JOBS = None
    def __init__(self, model=None, admin=False):
        
        self._JobManager = None
        self._JobSerializer = None
        
        if not isinstance(model, Model):
            raise TypeError("Workers must be initialized with django models")
        else:
            # this is to prevent a circular import that occurs!
            from django_framework.django_helpers.model_helpers import get_model_name
            self.model = model
            self.full_model_name, self.model_name = get_model_name(model=model)
            self.admin = admin
    
    @property
    def JobManager(self):
        if self._JobManager is None:
            self._JobManager = get_manager(manager_name="Job")
        return self._JobManager
    
    @property
    def JobSerializer(self):
        if self._JobSerializer is None:
            self._JobSerializer = get_serializer(serializer_name="Job", version = 'admin')
        return self._JobSerializer

    def get_job(self, query_params=None):
        
        if query_params is None:
            query_params = {}
        if "filter" not in query_params:
            query_params["filter"] = {}
            
        
        query_params["filter"].update(model_id=self.model.id, model_name=self.model_name)
        
        if query_params.get('order_by') == None:
            query_params["order_by"] = ['-created_at']
        
        

        return self.JobManager.get_by_query(query_params=query_params)
    
    
    
    def get_job_worker(self, command, action):
        
        if hasattr(self, 'job_worker') == False and self.job_worker == None:
            self.job_worker = self.ALLOWED_JOBS.find_job(command = self.command, action = self.action) # for now it's clean
        return self.job_worker
        
    def create_job(self, command=None, action=None, **kwargs):
        '''This will create a job by doing the following:
        1.  Validating that the job is correct
        2.  write a row into the Job table
        3.  if it is a synchronous job, it will then process the job. immediatly
        4.  return the job row
        '''

        # validate and make sure that it is a proper job
        job_worker = self.ALLOWED_JOBS.find_job(command = command, action = action)
        params = job_worker.validate_and_clean_job_request(command = command, action = action, **kwargs)
        
        
        # generate the initia payload
        initial_payload = self._generate_initial_payload(job_worker = job_worker, **kwargs) # by passing it to an internal method, makes it easier to subclass and override
        
        job_params = {
                      'model_name' : self.model_name,
                      'model_uuid' : str(self.model.uuid),
                      'model_id' : self.model.id,
                      'command'  : command,
                      'action'   : action,
                      'initial_payload' : json.dumps(initial_payload),
                      'job_timeout' : params['timeout'],
                      'timeout_at' : params['timeout_at'].timestamp,
                      'job_type' : params['job_type'],
                      'run_at' : params['run_at'],
                      }
        
        objs = self.JobManager.create(Serializer=self.JobSerializer, data=job_params)
        if objs[0].job_type == 'synchronous':
            objs = self.process_job_response(job_pk = objs[0].pk, response = None, job_model = objs[0])
        
        elif objs[0].job_type == 'asynchronous':
            # send to servers else where!
            self.send_asynchronous_job(job_model = objs[0])
            
        elif objs[0].job_type == 'local':
            # this is processed elsewhere!
            pass
        
        return objs
    
    def _generate_initial_payload(self, job_worker, **kwargs):
        # typically we want to just pass it stright to the job_worker.... but this makes it easier to override!
        return job_worker.generate_initial_payload(model = self.model, model_name=self.model_name, **kwargs)
    

    def process_job_response(self, job_pk, response = None, job_model = None):
        if job_model == None:
            job_model = self.JobManager.get_by_query(query_params = {'filter' : {'uuid' : job_pk}})[0]
        
        command = job_model.command 
        action  = job_model.action 
        # job_response here is an instance of a BaseWorkerResponse
        
        
        job_worker = self.ALLOWED_JOBS.find_job(command = command, action = action) # grab the relevant worker
        
        # we want to generate a response! # this response is an Object! to make sure it conforms, BaseWorkerResponse
        job_response = self._generate_response(job_worker = job_worker, job_model = job_model, response = response)

        # save the results!
        objs = self.JobManager.update(Serializer=self.JobSerializer, data=job_response.to_dict(is_json = True), model = job_model)
        
        # then process the results that you get! saving the various fields to the model etc.
        try:
            worker_response = job_response # for now
            job_update_response = self._process_response(job_worker = job_worker, job_model = job_model, worker_response = worker_response)
            
            if job_update_response.get('status') is None:
                job_update_response['status'] = 0
            job_update_response['completed_at'] = arrow.utcnow().timestamp
            
        except Exception as e:
            job_update_response = {'status' : -3, 'error_notes' : str(e)}
        
        if job_update_response != None:
            objs = self.JobManager.update(Serializer=self.JobSerializer, data= job_update_response, model = job_model)
            
        return objs

    def _generate_response(self, job_worker, job_model, response, **kwargs):
        # typically we want to just pass it stright to the job_worker.... but this makes it easier to override!
        return job_worker.generate_response(model = self.model, job_model = job_model, response = response)

    def _process_response(self, job_worker, job_model, worker_response, *args, **kwargs):
        # typically we want to just pass it stright to the job_worker.... but this makes it easier to override!
        
        job_response =job_worker.process_response(model = self.model, job_model = job_model, worker_response = worker_response)
        
        print('asdfasdfasdf', job_response)
        
        return job_response

#     def _set_job_response(self, response, job_model):
#         if job_model.job_type == 'synchronous' or job_model.job_type == 'local':
#             payload = BaseWorkerResponse(status = 3, response_payload = {'status' : 0, 'status_alt' : 'synchronous/local job pass through!'}, command = job_model.command, action = job_model.action, initial_payload = job_model.initial_payload, job_model = job_model, response_at = None)
#             
#             payload = self._set_job_response_payload(payload)
#         
#         else:
#             payload = BaseWorkerResponse(status = response.get('status'), response_payload = response, response_at = None)
#         
#         return payload
    
#     def validate_job(self, command, action, **kwargs):
#         
#         job_worker = self.get_job_worker(command = command, action = action)
#         params = job_worker.validate_and_clean_job_request(command = command, action = action, **kwargs)
#         return params
#     
#     
#     def _set_job_response_payload(self, job_response):
#         '''The JobResponse needs to have the .response_payload set properly! to match other inputs from other jobs'''
#         raise ValueError('This needs to be set for local/synchronous jobs!')
#         
#         
#         
#     
    
    def send_asynchronous_job(self, job_model):
        
        from django.conf import settings
        if settings.ALLOW_SEND_JOBS == True:
            response = requests.post(url = settings.SEND_JOB_URL, json = self.JobSerializer(job_model).data)
        
#             if response.status_code != 200:
#                 raise ValueError('The job that you requested was unable to be sent to our servers at this time:' + str(response.text))
            
        else:
            raise ValueError('This server is currently not allow any jobs to be sent!')
        
        pass
    