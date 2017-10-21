"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import BoardName_22
from snapp_email.datacontract.utils import export_dict, fill


class BoardName_22Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'BoardName_22'.
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: BoardName_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
        }
        endpoint = 'board'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.board.name-5.18+json',
            'Accept': 'application/vnd.4thoffice.board.name-5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(BoardName_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, boardId, impersonate_user_id=None, accept_type=None):
        """
        Retrieve board name.
        
        :param boardId: 
        :type boardId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: BoardName_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'boardId': boardId,
        }
        endpoint = 'board/{boardId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.board.name-5.18+json',
            'Accept': 'application/vnd.4thoffice.board.name-5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(BoardName_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def update(self, obj, boardId, impersonate_user_id=None, accept_type=None):
        """
        Update board name.
        
        :param obj: Object to be persisted
        :type obj: BoardName_22
        
        :param boardId: 
        :type boardId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: BoardName_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'boardId': boardId,
        }
        endpoint = 'board/{boardId}'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.board.name-5.18+json',
            'Accept': 'application/vnd.4thoffice.board.name-5.18+json' if accept_type is None else accept_type,
        }
        data = export_dict(obj)
        response = self.api_client.api_call('put', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=json.dumps(data))
        
        return fill(BoardName_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
