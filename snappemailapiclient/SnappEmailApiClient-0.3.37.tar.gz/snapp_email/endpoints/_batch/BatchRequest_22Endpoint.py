"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import BatchRequest_22
from snapp_email.datacontract.utils import export_dict, fill


class BatchRequest_22Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def create(self, obj, impersonate_user_id=None, accept_type=None):
        """
        
        
        :param obj: Object to be persisted
        :type obj: BatchRequest_22
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: BatchRequest_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'batch'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'multipart/mixed',
            'Accept': 'multipart/mixed' if accept_type is None else accept_type,
        }
        data = export_dict(obj)
        response = self.api_client.api_call('post', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=json.dumps(data))
        
        return fill(BatchRequest_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
