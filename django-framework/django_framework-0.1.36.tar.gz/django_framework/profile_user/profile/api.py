# this is where we hold basic things
from django_framework.django_helpers.api_helpers import BaseAPI
from django_framework.django_helpers.manager_helpers.manager_registry import get_manager
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer
 
 
from django.contrib.auth.models import User
 
from django_framework.helpers.security_helpers import generate_unique_key
import copy
 
class ProfileAPI(BaseAPI):
 
    def __init__(self, **kwargs):
        kwargs['run'] = False
         
        self.model_name = 'Profile'
        super(ProfileAPI, self).__init__(**kwargs)
 
    def default_login(self):
         pass
         