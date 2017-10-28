# coding=utf-8
import requests

import russell
from russell.exceptions import AuthenticationException
from russell.client.base import RussellHttpClient
from russell.model.user import User

class AuthClient(RussellHttpClient):
    """
    Auth/User specific client
    """
    def __init__(self):
        self.url = "/user"
        super(AuthClient, self).__init__()


    def get_user(self, access_token):
        user_dict = self.request("GET",url=self.url,
                                access_token=access_token)
        return User.from_dict(user_dict)
