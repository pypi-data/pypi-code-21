"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import LogOnUser_14
from snapp_email.datacontract.utils import export_dict, fill


class LogOnUser_14Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'LogOnUser_14'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: LogOnUser_14
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'user/session/logon'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.logon.user-v4.0+json',
            'Accept': 'application/vnd.4thoffice.logon.user-v4.0+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(LogOnUser_14, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def create(self, obj, impersonate_user_id=None, accept_type=None):
        """
        Perform login.
        
        :param obj: Object to be persisted
        :type obj: LogOnUser_14
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: LogOnUser_14
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'user/session/logon'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.logon.user-v4.0+json',
            'Accept': 'application/vnd.4thoffice.logon.user-v4.0+json' if accept_type is None else accept_type,
        }
        data = export_dict(obj)
        response = self.api_client.api_call('post', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=json.dumps(data))
        
        return fill(LogOnUser_14, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def delete(self, impersonate_user_id=None, accept_type=None):
        """
        Perform logout.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: True if object was deleted, otherwise an exception is raised
        :rtype: bool
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'user/session/logon'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.logon.user-v4.0+json',
            'Accept': 'application/vnd.4thoffice.logon.user-v4.0+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('delete', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return True
