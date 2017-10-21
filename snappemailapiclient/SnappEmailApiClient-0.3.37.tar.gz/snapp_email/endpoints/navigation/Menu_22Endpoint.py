"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import Menu_22
from snapp_email.datacontract.utils import export_dict, fill


class Menu_22Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'Menu_22'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: Menu_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'navigation'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.menu-v5.18+json',
            'Accept': 'application/vnd.4thoffice.menu-v5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(Menu_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, size, offset, menuScope=None, streamReadFilter=None, groupStreamOnly=None, applicationStreamOnly=None, returnFullResource=None, htmlFormat=None, impersonate_user_id=None, accept_type=None):
        """
        Get menu.
        
        :param size: Specify size of requested page.
        :type size: Int32
        
        :param offset: Specify offset of requested page.
        :type offset: Int32
        
        :param menuScope: Specify menu scope. Available values are: 'Important', 'Muted'.
        :type menuScope: String
        
        :param streamReadFilter: Search filter by stream read status. Available values are: 'All', 'Read', 'Unread'.
        :type streamReadFilter: String
        
        :param groupStreamOnly: Return group streams only.
        :type groupStreamOnly: Boolean
        
        :param applicationStreamOnly: Return application streams only.
        :type applicationStreamOnly: Boolean
        
        :param returnFullResource: Boolean flag indicating whether fully loaded resources should get returned.
        :type returnFullResource: Boolean
        
        :param htmlFormat: Mime format for html body of post resource.
            Available values:
            - text/html-stripped
            - text/html-stripped.mobile
        :type htmlFormat: String
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: Menu_22
        """
        url_parameters = {
            'menuScope': menuScope,
            'streamReadFilter': streamReadFilter,
            'groupStreamOnly': groupStreamOnly,
            'applicationStreamOnly': applicationStreamOnly,
            'returnFullResource': returnFullResource,
            'htmlFormat': htmlFormat,
            'size': size,
            'offset': offset,
        }
        endpoint_parameters = {
        }
        endpoint = 'navigation'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.menu-v5.18+json',
            'Accept': 'application/vnd.4thoffice.menu-v5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(Menu_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get_2(self, streamId, returnFullResource=None, impersonate_user_id=None, accept_type=None):
        """
        Get menu with selected items.
        
        :param streamId: Specify stream id
        :type streamId: String
        
        :param returnFullResource: Boolean flag indicating whether fully loaded resources should get returned.
        :type returnFullResource: Boolean
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: Menu_22
        """
        url_parameters = {
            'streamId': streamId,
            'returnFullResource': returnFullResource,
        }
        endpoint_parameters = {
        }
        endpoint = 'navigation'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.menu-v5.18+json',
            'Accept': 'application/vnd.4thoffice.menu-v5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(Menu_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
