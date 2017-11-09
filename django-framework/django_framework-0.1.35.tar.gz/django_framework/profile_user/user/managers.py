
from django_framework.django_helpers.manager_helpers.base_manager import BaseManager

from django_framework.django_helpers.manager_helpers.manager_registry import register_manager, get_manager

from django_framework.django_helpers.model_helpers.model_registry import get_model

from django_framework.helpers.security_helpers import md5_hasher

import copy
class UserManager(BaseManager):
    Model = get_model(model_name = 'User')

    @classmethod
    def create(cls, Serializer=None, data=None, clear_cache=True):
        cls.check_class_attributes_are_set()
        cls.check_serializer_class(serializer=Serializer)
        if data is None:
            data = {}

        serializer = cls.validate(Serializer=Serializer, data=data)
        if serializer:
            validated_data = serializer.validated_data
            # we need to do a check over the variables to determine if they are anything "special"
            # this includes ManyToManyField, ArrayField, JSONField, that are updated differently
            # So we remove those fields and let the "update" part deal with it
            validated_data_clean = copy.copy(validated_data)
            password = validated_data_clean.pop('password')
            
            obj = cls.Model.objects.create(**validated_data_clean)  # you cant update many to many like this...
            obj.set_password(raw_password = md5_hasher(password))
            obj.save()
        return [obj]
    
    @classmethod
    def _relationship_name_format(cls, relationship_name=None, relationship_list=None):

        if relationship_name == 'profile':
            ProfileManager = get_manager(manager_name = 'profile')
            profile = ProfileManager.get_by_query(query_params = {"filter" : {"id" : relationship_list[0]}})[0]

            query_key = 'id__in'
            relationship_list = [profile.user_id]
        
        return query_key, relationship_list


    @classmethod
    def _get_related_model(cls, models, relationship_name):
        '''This method allows us to get re'''
        if relationship_name == 'profile':
            ProfileManager = get_manager(manager_name = 'profile')
            user_ids = [model.id for model in models]
            models = ProfileManager.get_by_query(query_params = {'filter' : {'user_id__in' : user_ids}})

        else:
            raise ValueError('The relationship name requested was not understood')

        return models

register_manager(UserManager)
