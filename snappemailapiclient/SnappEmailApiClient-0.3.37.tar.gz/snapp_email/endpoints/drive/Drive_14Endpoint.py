"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import Drive_14
from snapp_email.datacontract.utils import export_dict, fill


class Drive_14Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'Drive_14'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: Drive_14
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'drive'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.drive-4.0+json',
            'Accept': 'application/vnd.4thoffice.drive-4.0+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(Drive_14, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, contextType, contextId, size, offset, filterItemId=None, sort=None, sortDirection=None, impersonate_user_id=None, accept_type=None):
        """
        Retrieve drive resource.
        
        :param contextType: Specify type of context. Available values are: 'User', 'Group', 'Discussion', 'Post', 'SyncApplication' and 'Stream'.
        :type contextType: ContextType_13
        
        :param contextId: Specify context id.
        :type contextId: String
        
        :param size: Specify size of requested page.
        :type size: Int32
        
        :param offset: Specify offset of requested page.
        :type offset: Int32
        
        :param filterItemId: Specify filter item id.
        :type filterItemId: String
        
        :param sort: Specify sort id.
        :type sort: String
        
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
        :rtype: Drive_14
        """
        url_parameters = {
            'contextType': contextType,
            'contextId': contextId,
            'filterItemId': filterItemId,
            'sort': sort,
            'sortDirection': sortDirection,
            'size': size,
            'offset': offset,
        }
        endpoint_parameters = {
        }
        endpoint = 'drive'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.drive-4.0+json',
            'Accept': 'application/vnd.4thoffice.drive-4.0+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(Drive_14, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
