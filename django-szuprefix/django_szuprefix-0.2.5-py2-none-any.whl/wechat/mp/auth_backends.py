import warnings

from django.contrib.auth.backends import ModelBackend
from . import helper

class WeiXinBackend(ModelBackend):
    """
    Custom auth backend that uses an email address and password

    For this to work, the User model must have an 'email' field
    """

    def authenticate(self, code):
        md = helper.api.login(code)
        return helper.api.get_or_create_wxuser(md).user
