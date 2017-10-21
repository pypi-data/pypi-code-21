"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import ThumbnailTextMapPage_19
from snapp_email.datacontract.utils import export_dict, fill


class ThumbnailTextMapPage_19Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, documentId, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'ThumbnailTextMapPage_19'.
        
        :param documentId: 
        :type documentId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ThumbnailTextMapPage_19
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'documentId': documentId,
        }
        endpoint = 'document/{documentId}/thumbnail'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.marg.bcsocial.thumbnail.text.map.page-v5.12+json',
            'Accept': 'application/vnd.marg.bcsocial.thumbnail.text.map.page-v5.12+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ThumbnailTextMapPage_19, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, documentId, thumbnailPage, size, offset, impersonate_user_id=None, accept_type=None):
        """
        Retrieve document thumbnail text map.
        
        :param documentId: 
        :type documentId: 
        
        :param thumbnailPage: Specify thumbnail page.
        :type thumbnailPage: Int32
        
        :param size: Specify size of requested page.
        :type size: Int32
        
        :param offset: Specify offset of requested page.
        :type offset: Int32
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ThumbnailTextMapPage_19
        """
        url_parameters = {
            'thumbnailPage': thumbnailPage,
            'size': size,
            'offset': offset,
        }
        endpoint_parameters = {
            'documentId': documentId,
        }
        endpoint = 'document/{documentId}/thumbnail'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.marg.bcsocial.thumbnail.text.map.page-v5.12+json',
            'Accept': 'application/vnd.marg.bcsocial.thumbnail.text.map.page-v5.12+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ThumbnailTextMapPage_19, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
