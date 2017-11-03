import arrow
import uuid

from django_framework.django_helpers.manager_helpers.base_manager import BaseManager

from django_framework.django_helpers.manager_helpers.manager_registry import register_manager, get_manager

from django_framework.django_helpers.model_helpers.model_registry import get_model
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer

from django_framework.django_helpers.manager_helpers.manager_registry import get_manager

from rest_framework import exceptions

from django_framework.helpers.security_helpers import encrypter

import json
from django.conf import settings
class AuthTokenManager(BaseManager):
    Model = get_model(model_name = 'AuthToken')

    @classmethod
    def create(cls, Serializer=None, data=None, clear_cache=True):
        if data is None:
            data = {}
        data['expire_at'] = arrow.utcnow().replace(months =+ 1).timestamp
# 
        return super(AuthTokenManager, cls).create(Serializer=Serializer, data=data, clear_cache=True)

    @classmethod
    def refresh_token(cls, model = None, clear_cache=True):
        data = {}
        data['current_token'] = uuid.uuid4()
        data['expire_at'] = arrow.utcnow().replace(months =+ 1).timestamp
        
        Serializer = get_serializer('AuthToken', version = 'admin')
        response = super(AuthTokenManager, cls).update(Serializer = Serializer, data = data, model = model, clear_cache=clear_cache)
        
        
        
        return response

    @classmethod
    def authenticate(cls, user_id, token):
        '''The goal here is to add in some cache fetching and setting logic so we dont hit the DB everytime...
        will also need to deal with refreshing a token...'''
        # version 1 
        cache = cls.get_cache(key = 'auth:' + token)
        is_valid_token = cache.get() # return True, False or None
#         is_valid_token= None
        if is_valid_token == None:
            query_params = {'filter': {'user_id': user_id,'current_token' : token, 'expire_at__gte': arrow.utcnow()}}
            token = cls.get_by_query(query_params = query_params)
            
            if len(token) == 1:
                is_valid_token = True
            
            response = cache.set(value = is_valid_token, ttl = 1800)
        return is_valid_token

    @classmethod
    def get_auth_token(cls, auth_token, profile = None):
        '''WARNING:  WHEN UPDATING THIS METHOD PLEASE CHECK THE auth_token section to make corresponding updates to information being passed!'''
        
        user = auth_token.user
        if profile == None:
            ProfileManager = get_manager('profile')
            profile = ProfileManager.get_by_query({'filter' : {'user_id' : user.id}})[0]

        data = {"user_id" : user.id, 
                "user_is_staff" : user.is_staff, 
                "profile_id" : profile.id, 
                "profile_uuid" : str(profile.uuid), 
                "expire_at" : arrow.get(auth_token.expire_at).timestamp, 
                "current_token" : str(auth_token.current_token) }
        
        
        token = encrypter(astr = json.dumps(data), des_key = settings.PRIVATE_TRIPLE_DES_TOKEN_KEY)
        return token


    @classmethod
    def _relationship_name_format(cls, relationship_name=None, relationship_list=None):
        if relationship_name == 'profile':
            ProfileManager = get_manager(manager_name = 'profile')
            profile = ProfileManager.get_by_query(query_params = {"filter" : {"id" : relationship_list[0]}})[0]
            
            
            query_key = 'user_id__in'
            relationship_list = [profile.user_id]
        
        return query_key, relationship_list
    
    @classmethod
    def _get_related_model(cls, models, relationship_name):
        '''This method allows us to get re'''
        if relationship_name == 'profile':
            user_ids = [model.user.id for model in models]
            ProfileManager = get_manager(manager_name = 'profile')
            models = ProfileManager.get_by_query(query_params = {"filter" : {"user_id__in" : user_ids}})
        else:
            raise ValueError('The relationship name requested was not understood')

        return models


    
register_manager(AuthTokenManager)
