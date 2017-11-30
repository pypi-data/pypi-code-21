import arrow
import json
import copy
import requests
from django.db.models import Model

from django_framework.django_helpers.manager_helpers import get_manager
from django_framework.django_helpers.serializer_helpers import get_serializer



from base_worker_response import BaseWorkerResponse

class BaseWorker(object):
    # async jobs are sent to another server
    # sync jobs are processed IMMEDIATELY
    # local is processed on local server using management tools

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
        '''This get's the actual job rows for the given query_params'''
        if query_params is None:
            query_params = {}
        if "filter" not in query_params:
            query_params["filter"] = {}
            
        
        query_params["filter"].update(model_id=self.model.id, model_name=self.model_name)
        
        if query_params.get('order_by') == None:
            query_params["order_by"] = ['-created_at']
        
        

        return self.JobManager.get_by_query(query_params=query_params)
    
    
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
        
        
        initial_payload = self.generate_initial_payload(command = command, action = action, **kwargs)
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
        
        #create the row in the DB in the jobs table
        objs = self.JobManager.create(Serializer=self.JobSerializer, data=job_params)
        
        # do appropriate action from the job
        if objs[0].job_type == 'synchronous':
            objs = self.process_job_response(job_pk = objs[0].pk, response = None, job_model = objs[0])
        
        elif objs[0].job_type == 'asynchronous':
            # send to servers else where!
            self.send_asynchronous_job(job_model = objs[0])
        elif objs[0].job_type == 'local' :
            # local jobs are dealth with later!
            pass
        return objs
    
    def process_job_response(self, job_pk, response = None, job_model = None):
        if job_model == None:
            job_model = self.JobManager.get_by_query(query_params = {'filter' : {'uuid' : job_pk}})[0]
        
        
        # job_response here is an instance of a BaseWorkerResponse
        job_response = self._set_job_response(response = response, job_model = job_model)

        # you cannot serialize to JSON in the validator since DRF errors out before even getting to Serializer Validations
        # apperently, wrong type (dict vs str) check is checked first.
        
        objs = self.JobManager.update(Serializer=self.JobSerializer, data=job_response.to_dict(is_json = True), model = job_model)
        try:
            job_update_response = self.process_response(worker_response = job_response)
        except Exception as e:
            job_update_response = {'status' : -3, 'error_notes' : str(e)}
        
        if job_update_response != None:
            objs = self.JobManager.update(Serializer=self.JobSerializer, data= job_update_response, model = job_model)
            
        return objs
    
    def _set_job_response(self, response, job_model):
        if job_model.job_type == 'synchronous' or job_model.job_type == 'local':
            payload = BaseWorkerResponse(status = 3, response_payload = {'status' : 0, 'status_alt' : 'synchronous/local job pass through!'}, command = job_model.command, action = job_model.action, initial_payload = job_model.initial_payload, job_model = job_model, response_at = None)
            
            payload = self._set_job_response_payload(payload)
        
        else:
            payload = BaseWorkerResponse(status = response.get('status'), response_payload = response, response_at = None)
        
        return payload
    
    def validate_job(self, command, action, **kwargs):
        
        job_worker = self.ALLOWED_JOBS.find_job(command = command, action = action)
        params = job_worker.validate_and_clean_job_request(command = command, action = action, **kwargs)
        return params
    
    
    def _set_job_response_payload(self, job_response):
        '''The JobResponse needs to have the .response_payload set properly! to match other inputs from other jobs'''
        raise ValueError('This needs to be set for local/synchronous jobs!')
        
        
        
    
    def send_asynchronous_job(self, job_model):
        
        from django.conf import settings
        if settings.ALLOW_SEND_JOBS == True:
            response = requests.post(url = settings.SEND_JOB_URL, json = self.JobSerializer(job_model).data)
        
#             if response.status_code != 200:
#                 raise ValueError('The job that you requested was unable to be sent to our servers at this time:' + str(response.text))
            
        else:
            raise ValueError('This server is currently not allow any jobs to be sent!')
        
        pass
    
    
    def generate_initial_payload(self, command, action, **kwargs):
        raise NotImplemented('Please implement me!')
    
    
    def process_response(self, worker_response):
        raise NotImplemented('Please implement me!')