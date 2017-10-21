"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import ListOfClientEventLogs_15
from snapp_email.datacontract.utils import export_dict, fill


class ListOfClientEventLogs_15Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'ListOfClientEventLogs_15'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfClientEventLogs_15
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'event'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.client.event.log.list-5.0+json',
            'Accept': 'application/vnd.4thoffice.client.event.log.list-5.0+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ListOfClientEventLogs_15, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def create(self, obj, impersonate_user_id=None, accept_type=None):
        """
        Post event log from client side.
        
        :param obj: Object to be persisted
        :type obj: ListOfClientEventLogs_15
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfClientEventLogs_15
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'event'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.client.event.log.list-5.0+json',
            'Accept': 'application/vnd.4thoffice.client.event.log.list-5.0+json' if accept_type is None else accept_type,
        }
        data = export_dict(obj)
        response = self.api_client.api_call('post', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=json.dumps(data))
        
        return fill(ListOfClientEventLogs_15, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
