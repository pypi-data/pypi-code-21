"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import ListOfSignaturesPage_20
from snapp_email.datacontract.utils import export_dict, fill


class ListOfSignaturesPage_20Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'ListOfSignaturesPage_20'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfSignaturesPage_20
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'signature'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.signature.list.page-5.15+json',
            'Accept': 'application/vnd.4thoffice.signature.list.page-5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ListOfSignaturesPage_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, signatureId, size, offset, suggestions=None, impersonate_user_id=None, accept_type=None):
        """
        Retrieve signature resource
        
        :param signatureId: 
        :type signatureId: 
        
        :param size: Specify size of requested page.
        :type size: Int32
        
        :param offset: Specify offset of requested page.
        :type offset: Int32
        
        :param suggestions: Return recognized signatures as suggestions
        :type suggestions: Boolean
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfSignaturesPage_20
        """
        url_parameters = {
            'suggestions': suggestions,
            'size': size,
            'offset': offset,
        }
        endpoint_parameters = {
            'signatureId': signatureId,
        }
        endpoint = 'signature/{signatureId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.signature.list.page-5.15+json',
            'Accept': 'application/vnd.4thoffice.signature.list.page-5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ListOfSignaturesPage_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
