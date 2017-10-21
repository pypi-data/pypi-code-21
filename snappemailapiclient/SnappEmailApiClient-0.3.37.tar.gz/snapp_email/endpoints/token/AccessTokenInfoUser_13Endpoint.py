"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import AccessTokenInfoUser_13
from snapp_email.datacontract.utils import export_dict, fill


class AccessTokenInfoUser_13Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'AccessTokenInfoUser_13'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: AccessTokenInfoUser_13
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'token'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.marg.bcsocial.access.token.info.user-3.6+json',
            'Accept': 'application/vnd.marg.bcsocial.access.token.info.user-3.6+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(AccessTokenInfoUser_13, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, accessToken, impersonate_user_id=None, accept_type=None):
        """
        Get user settings resource.
        
        :param accessToken: Specify access token.
        :type accessToken: String
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: AccessTokenInfoUser_13
        """
        url_parameters = {
            'accessToken': accessToken,
        }
        endpoint_parameters = {
        }
        endpoint = 'token'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.marg.bcsocial.access.token.info.user-3.6+json',
            'Accept': 'application/vnd.marg.bcsocial.access.token.info.user-3.6+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(AccessTokenInfoUser_13, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
