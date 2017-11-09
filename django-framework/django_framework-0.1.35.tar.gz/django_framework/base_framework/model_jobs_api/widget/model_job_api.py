
import copy
from django_framework.django_helpers.api_helpers import BaseAPI


from django_framework.django_helpers.model_helpers import get_model
from django_framework.django_helpers.serializer_helpers import get_serializer
from django_framework.django_helpers.manager_helpers import get_manager
from django_framework.django_helpers.meta_helpers import get_meta

from django_framework.django_helpers.api_helpers import get_api

ModelAPI = get_api('ModelAPI')

class ModelJobAPI(ModelAPI):
    
    def __init__(self, request, model_name, job_pk = None, admin = False, **kwargs):
        super(ModelJobAPI, self).__init__(request=request, model_name = model_name, admin = admin, **kwargs)
        
        self.job_pk = job_pk
        self.WorkerMeta = get_meta(meta_name = 'job')
        self.WorkerSerializer = get_serializer(serializer_name = 'job', version = self.version)


    def get(self):
        '''Get Jobs that are associated with the provided model.  It may return a list of jobs, or the one specified.'''
        model_worker = self.get_model_worker()
        query_params = self.query_params
        if self.job_pk is not None:
            if query_params.get('filter') == None:
                query_params['filter'] = {}

            query_params['filter'].update({'uuid' : self.job_pk})

        objs = model_worker.get_job(query_params = query_params )
        
        return objs
    
    def post(self):
        '''Create a new job for the given model'''
        model_worker = self.get_model_worker()
        objs = model_worker.create_job(**self.query_data)
        return objs
    
    
    def put(self):
        '''Update a given job.  This is treated as an  "response" and can cause other affects.'''
        model_worker = self.get_model_worker()
        objs = model_worker.process_job_response(job_pk = self.job_pk, response = self.query_data)
        return objs

    def delete(self):
        '''Deleting a job.  You cannot do this.'''
        raise NotImplementedError('You are not allowed to delete jobs!')


    def get_model_worker(self):
        '''Get the worker class for a given type of model.  The worker class can then be used to get the Jobs associated 
        for a specified model.'''
        
        self.WorkerMeta.allowed_method(method = self.request.method, version = self.version, user_job = True)
        objs = self.get_model_with_permissions()

        if len(objs) == 1:
            model_worker = objs[0].get_worker()
        
        else:
            raise ValueError('No worker or too many workers could be found for specified model!  This is an error!')

        return model_worker
    
    def format_data(self, data):
        '''Serializes data and paginate data. Includes meta data as well.'''
        meta_data = { "total_query_results" : len(data),
                      "type" : self.model_name + 'Job'
                     }
        
        if self.request_method == 'DELETE':
            pass
        else:
            data = self.serialize_data(data = self._paginate(data))
        return dict(data=data, meta_data = meta_data)
    

    def serialize_data(self, data):
        return self.WorkerSerializer(self._paginate(data), many=True).data
    
    
    

