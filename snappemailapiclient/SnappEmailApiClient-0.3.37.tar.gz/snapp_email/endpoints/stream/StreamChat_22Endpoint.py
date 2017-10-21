"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import StreamChat_22
from snapp_email.datacontract.utils import export_dict, fill


class StreamChat_22Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'StreamChat_22'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: StreamChat_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'stream'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.stream.chat-5.18+json',
            'Accept': 'application/vnd.4thoffice.stream.chat-5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(StreamChat_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, streamId, size, offset, sinceId=None, sortDirection=None, impersonate_user_id=None, accept_type=None):
        """
        Get stream chat posts.
        
        :param streamId: 
        :type streamId: 
        
        :param size: Specify size of requested page.
        :type size: Int32
        
        :param offset: Specify offset of requested page.
        :type offset: Int32
        
        :param sinceId: Specify since id. That is an id of a resource from which incremental list load should take place.
        :type sinceId: String
        
        :param sortDirection: Specify sort direction.
            Available values:
            - Ascending
            - Descending
        :type sortDirection: String
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: StreamChat_22
        """
        url_parameters = {
            'sinceId': sinceId,
            'sortDirection': sortDirection,
            'size': size,
            'offset': offset,
        }
        endpoint_parameters = {
            'streamId': streamId,
        }
        endpoint = 'stream/{streamId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.stream.chat-5.18+json',
            'Accept': 'application/vnd.4thoffice.stream.chat-5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(StreamChat_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
