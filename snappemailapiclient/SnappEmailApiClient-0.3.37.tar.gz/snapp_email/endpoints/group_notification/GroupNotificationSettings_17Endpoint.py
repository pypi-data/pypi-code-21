"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import GroupNotificationSettings_17
from snapp_email.datacontract.utils import export_dict, fill


class GroupNotificationSettings_17Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, groupId, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'GroupNotificationSettings_17'.
        
        :param groupId: 
        :type groupId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: GroupNotificationSettings_17
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'groupId': groupId,
        }
        endpoint = 'group/{groupId}/notification'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.group.notification.settings-5.3+json',
            'Accept': 'application/vnd.4thoffice.group.notification.settings-5.3+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(GroupNotificationSettings_17, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, groupId, impersonate_user_id=None, accept_type=None):
        """
        Get group notification settings.
        
        :param groupId: 
        :type groupId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: GroupNotificationSettings_17
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'groupId': groupId,
        }
        endpoint = 'group/{groupId}/notification'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.group.notification.settings-5.3+json',
            'Accept': 'application/vnd.4thoffice.group.notification.settings-5.3+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(GroupNotificationSettings_17, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def update(self, obj, groupId, impersonate_user_id=None, accept_type=None):
        """
        Update group notification settings.
        
        :param obj: Object to be persisted
        :type obj: GroupNotificationSettings_17
        
        :param groupId: 
        :type groupId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: GroupNotificationSettings_17
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'groupId': groupId,
        }
        endpoint = 'group/{groupId}/notification'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.group.notification.settings-5.3+json',
            'Accept': 'application/vnd.4thoffice.group.notification.settings-5.3+json' if accept_type is None else accept_type,
        }
        data = export_dict(obj)
        response = self.api_client.api_call('put', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=json.dumps(data))
        
        return fill(GroupNotificationSettings_17, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
