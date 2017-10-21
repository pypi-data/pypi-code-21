"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import DocumentThumbnailInfo_13
from snapp_email.datacontract.utils import export_dict, fill


class DocumentThumbnailInfo_13Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, documentId, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'DocumentThumbnailInfo_13'.
        
        :param documentId: 
        :type documentId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: DocumentThumbnailInfo_13
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'documentId': documentId,
        }
        endpoint = 'document/{documentId}/thumbnail'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.marg.bcsocial.document.thumbnail.info-v3.6+json',
            'Accept': 'application/vnd.marg.bcsocial.document.thumbnail.info-v3.6+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(DocumentThumbnailInfo_13, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, documentId, impersonate_user_id=None, accept_type=None):
        """
        Retrieve document thumbnail info.
        
        :param documentId: 
        :type documentId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: DocumentThumbnailInfo_13
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'documentId': documentId,
        }
        endpoint = 'document/{documentId}/thumbnail'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.marg.bcsocial.document.thumbnail.info-v3.6+json',
            'Accept': 'application/vnd.marg.bcsocial.document.thumbnail.info-v3.6+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(DocumentThumbnailInfo_13, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
