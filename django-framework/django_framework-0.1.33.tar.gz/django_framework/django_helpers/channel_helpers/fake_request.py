
import json
from django_framework.django_helpers.token_auth_helper import TokenAuthentication

class FakeRequest(object):
    def __init__(self, **kwargs):
        
        self.message = kwargs.get('message')
        
        self.path = self.message.content['path'] 
        self.method = self.message.content['method']
        self.original_data = self.message.content['data']
        self.original_query_params = self.message.content['query_params']
        
        self.data = self.original_data
        self.query_params = self.original_query_params
        
        
        if self.query_params == None:
            self.query_params = {}

        
        self.headers = self.message.content['headers']
        
        self.META = {
            'HTTP_AUTHORIZATION' : self.headers['HTTP_AUTHORIZATION'],
            'QUERY_STRING' : self.query_params
            }

        self.user = None #User.objects.get(id = 1)
        self.set_user()

    def get_full_path(self):
        '''This is used to cache.  This means it needs to include the proper query params!'''
        if type(self.query_params) == dict:
            if len(self.query_params) == 0:
                full_path = self.path
            else:
                full_path = self.path + json.dumps(self.query_params)
        elif type(self.query_params) == None:
            full_path = self.path
            
        else:
            full_path = self.path + self.query_params
        
        return full_path
    
    
    
    
    def set_user(self):
        
        user, token = TokenAuthentication().authenticate(request = self)
        self.user = user
        
        
class FakeResponse(object):
    
    def __init__(self, original_request, response):
        
        self.original_request = original_request
        self.pre_response = response
        
        self.response = self.pre_response
        self.response['meta_data']['request_url'] = self.original_request.get_full_path()
        self.status_code = 200

    def get_response(self):
        return self.response
    
    