"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import ListOfPostsPage_22
from snapp_email.datacontract.utils import export_dict, fill


class ListOfPostsPage_22Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'ListOfPostsPage_22'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfPostsPage_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'post'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.post.list.page-5.18+json',
            'Accept': 'application/vnd.4thoffice.post.list.page-5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ListOfPostsPage_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, postId, size, offset, EmailMessageId=None, impersonate_user_id=None, accept_type=None):
        """
        Retrieve list of post resources.
        
        :param postId: 
        :type postId: 
        
        :param size: Specify size of requested page.
        :type size: Int32
        
        :param offset: Specify offset of requested page.
        :type offset: Int32
        
        :param EmailMessageId: Specify mail message id.
        :type EmailMessageId: String
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfPostsPage_22
        """
        url_parameters = {
            'EmailMessageId': EmailMessageId,
            'size': size,
            'offset': offset,
        }
        endpoint_parameters = {
            'postId': postId,
        }
        endpoint = 'post/{postId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.post.list.page-5.18+json',
            'Accept': 'application/vnd.4thoffice.post.list.page-5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ListOfPostsPage_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
