"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import StreamAssistant_22
from snapp_email.datacontract.utils import export_dict, fill


class StreamAssistant_22Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'StreamAssistant_22'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: StreamAssistant_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'stream'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.stream.assistant-5.18+json',
            'Accept': 'application/vnd.4thoffice.stream.assistant-5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(StreamAssistant_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, streamId, impersonate_user_id=None, accept_type=None):
        """
        Get stream assistant posts.
        
        :param streamId: 
        :type streamId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: StreamAssistant_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'streamId': streamId,
        }
        endpoint = 'stream/{streamId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.stream.assistant-5.18+json',
            'Accept': 'application/vnd.4thoffice.stream.assistant-5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(StreamAssistant_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def update(self, obj, streamId, impersonate_user_id=None, accept_type=None):
        """
        Update stream assistant resource.
        
        :param obj: Object to be persisted
        :type obj: StreamAssistant_22
        
        :param streamId: 
        :type streamId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: StreamAssistant_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'streamId': streamId,
        }
        endpoint = 'stream/{streamId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.stream.assistant-5.18+json',
            'Accept': 'application/vnd.4thoffice.stream.assistant-5.18+json' if accept_type is None else accept_type,
        }
        data = export_dict(obj)
        response = self.api_client.api_call('put', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=json.dumps(data))
        
        return fill(StreamAssistant_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def delete(self, streamId, flagServiceId, impersonate_user_id=None, accept_type=None):
        """
        Delete stream assistant resource.
        
        :param streamId: 
        :type streamId: 
        
        :param flagServiceId: Flag service id for stream assistant.
        :type flagServiceId: String
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: True if object was deleted, otherwise an exception is raised
        :rtype: bool
        """
        url_parameters = {
            'flagServiceId': flagServiceId,
        }
        endpoint_parameters = {
            'streamId': streamId,
        }
        endpoint = 'stream/{streamId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.stream.assistant-5.18+json',
            'Accept': 'application/vnd.4thoffice.stream.assistant-5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('delete', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return True
