"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import ActionableResource_20
from snapp_email.datacontract.utils import export_dict, fill


class ActionableResource_20Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'ActionableResource_20'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ActionableResource_20
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'action'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.actionable.resource-v5.15+json',
            'Accept': 'application/vnd.4thoffice.actionable.resource-v5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ActionableResource_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, actionableResourceId, contextType=None, contextId=None, impersonate_user_id=None, accept_type=None):
        """
        Retrieve actionable resource.
        
        :param actionableResourceId: 
        :type actionableResourceId: 
        
        :param contextType: Specify type of context. Available values are: 'Discussion', 'NewPost', 'Post', 'Stream', 'ChatStream', 'GroupList', 'File', 'BoardList', 'ReminderList', 'StreamList', 'StreamListMuted', 'StreamListImportant', 'StreamListImportantUnread'.
        :type contextType: String
        
        :param contextId: Specify context id.
        :type contextId: String
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ActionableResource_20
        """
        url_parameters = {
            'contextType': contextType,
            'contextId': contextId,
        }
        endpoint_parameters = {
            'actionableResourceId': actionableResourceId,
        }
        endpoint = 'action/{actionableResourceId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.actionable.resource-v5.15+json',
            'Accept': 'application/vnd.4thoffice.actionable.resource-v5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ActionableResource_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def create(self, obj, impersonate_user_id=None, accept_type=None):
        """
        Create arbitrary action.
        
        :param obj: Object to be persisted
        :type obj: ActionableResource_20
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ActionableResource_20
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'action'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.actionable.resource-v5.15+json',
            'Accept': 'application/vnd.4thoffice.actionable.resource-v5.15+json' if accept_type is None else accept_type,
        }
        data = export_dict(obj)
        response = self.api_client.api_call('post', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=json.dumps(data))
        
        return fill(ActionableResource_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
