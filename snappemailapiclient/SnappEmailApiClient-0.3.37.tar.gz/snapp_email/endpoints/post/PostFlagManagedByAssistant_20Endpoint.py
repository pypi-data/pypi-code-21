"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import PostFlagManagedByAssistant_20
from snapp_email.datacontract.utils import export_dict, fill


class PostFlagManagedByAssistant_20Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'PostFlagManagedByAssistant_20'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: PostFlagManagedByAssistant_20
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'post'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.post.flag.managed.by.assistant-v5.15+json',
            'Accept': 'application/vnd.4thoffice.post.flag.managed.by.assistant-v5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(PostFlagManagedByAssistant_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, postId, impersonate_user_id=None, accept_type=None):
        """
        Retrieve status indicating if resource has beed managed by assistant.
        
        :param postId: 
        :type postId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: PostFlagManagedByAssistant_20
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'postId': postId,
        }
        endpoint = 'post/{postId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.post.flag.managed.by.assistant-v5.15+json',
            'Accept': 'application/vnd.4thoffice.post.flag.managed.by.assistant-v5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(PostFlagManagedByAssistant_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def update(self, obj, postId, impersonate_user_id=None, accept_type=None):
        """
        Update status indicating if resource has beed managed by assistant.
        
        :param obj: Object to be persisted
        :type obj: PostFlagManagedByAssistant_20
        
        :param postId: 
        :type postId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: PostFlagManagedByAssistant_20
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'postId': postId,
        }
        endpoint = 'post/{postId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.post.flag.managed.by.assistant-v5.15+json',
            'Accept': 'application/vnd.4thoffice.post.flag.managed.by.assistant-v5.15+json' if accept_type is None else accept_type,
        }
        data = export_dict(obj)
        response = self.api_client.api_call('put', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=json.dumps(data))
        
        return fill(PostFlagManagedByAssistant_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
