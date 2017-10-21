"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import BoardAvatar_22
from snapp_email.datacontract.utils import export_dict, fill


class BoardAvatar_22Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, boardId, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'BoardAvatar_22'.
        
        :param boardId: 
        :type boardId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: BoardAvatar_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'boardId': boardId,
        }
        endpoint = 'board/{boardId}/avatar'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.board.avatar-5.18+json',
            'Accept': 'application/vnd.4thoffice.board.avatar-5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(BoardAvatar_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, boardId, imageSize=None, impersonate_user_id=None, accept_type=None):
        """
        Get board avatar.
        
        :param boardId: 
        :type boardId: 
        
        :param imageSize: Specify size in [px], avatar image should get resized/cropped to.
        :type imageSize: Int32
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: BoardAvatar_22
        """
        url_parameters = {
            'imageSize': imageSize,
        }
        endpoint_parameters = {
            'boardId': boardId,
        }
        endpoint = 'board/{boardId}/avatar'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.board.avatar-5.18+json',
            'Accept': 'application/vnd.4thoffice.board.avatar-5.18+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(BoardAvatar_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def update(self, obj, boardId, impersonate_user_id=None, accept_type=None):
        """
        Update board avatar.
        
        :param obj: Object to be persisted
        :type obj: BoardAvatar_22
        
        :param boardId: 
        :type boardId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: BoardAvatar_22
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'boardId': boardId,
        }
        endpoint = 'board/{boardId}/avatar'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.board.avatar-5.18+json',
            'Accept': 'application/vnd.4thoffice.board.avatar-5.18+json' if accept_type is None else accept_type,
        }
        data = export_dict(obj)
        response = self.api_client.api_call('put', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=json.dumps(data))
        
        return fill(BoardAvatar_22, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
