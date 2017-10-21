"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import Document_18
from snapp_email.datacontract.utils import export_dict, fill


class Document_18Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'Document_14'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: Document_18
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'document'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.document-v5.8+json',
            'Accept': 'application/vnd.4thoffice.document-v5.8+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(Document_18, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, documentId, impersonate_user_id=None, accept_type=None):
        """
        Retrieve document.
        
        :param documentId: 
        :type documentId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: Document_18
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'documentId': documentId,
        }
        endpoint = 'document/{documentId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.document-v5.8+json',
            'Accept': 'application/vnd.4thoffice.document-v5.8+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        if accept_type == 'application/octet-stream' or accept_type.startswith('image/'):
            return response.content
        return fill(Document_18, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def create(self, obj, obj_filename, impersonate_user_id=None, accept_type=None):
        """
        Create document.
        
        :param obj: Object to be persisted
        :type obj: 
        
        :param obj_filename: Filename of object to be persisted
        :type obj_filename: str
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: Document_18
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'document'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/octet-stream',
            'Accept': 'application/vnd.4thoffice.document-v5.8+json' if accept_type is None else accept_type,
            'X-Upload-File-Name': obj_filename,
        }
        response = self.api_client.api_call('post', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=obj)
        
        return fill(Document_18, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
