"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import ListOfBoardsPage_20
from snapp_email.datacontract.utils import export_dict, fill


class ListOfBoardsPage_20Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'ListOfBoardsPage_20'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfBoardsPage_20
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'board'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.board.list.page-v5.15+json',
            'Accept': 'application/vnd.4thoffice.board.list.page-v5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ListOfBoardsPage_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, boardId, size, offset, impersonate_user_id=None, accept_type=None):
        """
        Retrieve list of board resources.
        
        :param boardId: 
        :type boardId: 
        
        :param size: Specify size of requested page.
        :type size: Int32
        
        :param offset: Specify offset of requested page.
        :type offset: Int32
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: ListOfBoardsPage_20
        """
        url_parameters = {
            'size': size,
            'offset': offset,
        }
        endpoint_parameters = {
            'boardId': boardId,
        }
        endpoint = 'board/{boardId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.board.list.page-v5.15+json',
            'Accept': 'application/vnd.4thoffice.board.list.page-v5.15+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(ListOfBoardsPage_20, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
