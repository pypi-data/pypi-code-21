"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import Group_17
from snapp_email.datacontract.utils import export_dict, fill


class Group_17Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'Group_17'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: Group_17
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'group'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.group-5.3+json',
            'Accept': 'application/vnd.4thoffice.group-5.3+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(Group_17, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, groupId, impersonate_user_id=None, accept_type=None):
        """
        Get user group.
        
        :param groupId: 
        :type groupId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: Group_17
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'groupId': groupId,
        }
        endpoint = 'group/{groupId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.group-5.3+json',
            'Accept': 'application/vnd.4thoffice.group-5.3+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(Group_17, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def create(self, obj, impersonate_user_id=None, accept_type=None):
        """
        Create user group.
        
        :param obj: Object to be persisted
        :type obj: Group_17
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: Group_17
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'group'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.group-5.3+json',
            'Accept': 'application/vnd.4thoffice.group-5.3+json' if accept_type is None else accept_type,
        }
        data = export_dict(obj)
        response = self.api_client.api_call('post', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=json.dumps(data))
        
        return fill(Group_17, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def update(self, obj, groupId, impersonate_user_id=None, accept_type=None):
        """
        Update user group.
        
        :param obj: Object to be persisted
        :type obj: Group_17
        
        :param groupId: 
        :type groupId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: Group_17
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'groupId': groupId,
        }
        endpoint = 'group/{groupId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.group-5.3+json',
            'Accept': 'application/vnd.4thoffice.group-5.3+json' if accept_type is None else accept_type,
        }
        data = export_dict(obj)
        response = self.api_client.api_call('put', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=json.dumps(data))
        
        return fill(Group_17, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def delete(self, groupId, impersonate_user_id=None, accept_type=None):
        """
        Delete user group.
        
        :param groupId: 
        :type groupId: 
        
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
            'groupId': groupId,
        }
        endpoint = 'group/{groupId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.group-5.3+json',
            'Accept': 'application/vnd.4thoffice.group-5.3+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('delete', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return True
