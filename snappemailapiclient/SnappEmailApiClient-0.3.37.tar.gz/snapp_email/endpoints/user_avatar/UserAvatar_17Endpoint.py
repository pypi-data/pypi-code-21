"""
Auto generated code

"""

import json
from snapp_email.datacontract.classes import UserAvatar_17
from snapp_email.datacontract.utils import export_dict, fill


class UserAvatar_17Endpoint:
    def __init__(self, api_client):
        self.api_client = api_client
    
    def options(self, userId, impersonate_user_id=None, accept_type=None):
        """
        Retrieve options available for resource 'UserAvatar_17'.
        
        :param userId: 
        :type userId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: UserAvatar_17
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'userId': userId,
        }
        endpoint = 'user/{userId}/avatar'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.user.avatar-5.3+json',
            'Accept': 'application/vnd.4thoffice.user.avatar-5.3+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('options', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        
        return fill(UserAvatar_17, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def get(self, userId, imageSize=None, impersonate_user_id=None, accept_type=None):
        """
        Get user avatar.
        
        :param userId: 
        :type userId: 
        
        :param imageSize: Specify size in [px], avatar image should get resized/cropped to.
        :type imageSize: Int32
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: UserAvatar_17
        """
        url_parameters = {
            'imageSize': imageSize,
        }
        endpoint_parameters = {
            'userId': userId,
        }
        endpoint = 'user/{userId}/avatar'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/vnd.4thoffice.user.avatar-5.3+json',
            'Accept': 'application/vnd.4thoffice.user.avatar-5.3+json' if accept_type is None else accept_type,
        }
        response = self.api_client.api_call('get', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id)
        if accept_type == 'application/octet-stream' or accept_type.startswith('image/'):
            return response.content
        return fill(UserAvatar_17, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
    
    def update(self, obj, obj_filename, userId, impersonate_user_id=None, accept_type=None):
        """
        Update user avatar.
        
        :param obj: Object to be persisted
        :type obj: 
        
        :param obj_filename: Filename of object to be persisted
        :type obj_filename: str
        
        :param userId: 
        :type userId: 
        
        :param impersonate_user_id: 
        :type impersonate_user_id: str
        
        :param accept_type: 
        :type accept_type: str
        
        :return: 
        :rtype: UserAvatar_17
        """
        url_parameters = {
        }
        endpoint_parameters = {
            'userId': userId,
        }
        endpoint = 'user/{userId}/avatar'.format(**endpoint_parameters)
        add_headers = {
            'Content-Type': 'application/octet-stream',
            'Accept': 'application/vnd.4thoffice.user.avatar-5.3+json' if accept_type is None else accept_type,
            'X-Upload-File-Name': obj_filename,
        }
        response = self.api_client.api_call('put', endpoint, url_parameters, add_headers, impersonate_user_id=impersonate_user_id, data=obj)
        
        return fill(UserAvatar_17, response.json(), content_type=response.headers['Content-Type'], silence_exceptions=self.api_client.silence_fill_exceptions)
