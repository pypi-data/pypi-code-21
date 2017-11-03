
from django_framework.django_helpers.manager_helpers.base_manager import BaseManager

from django_framework.django_helpers.manager_helpers.manager_registry import register_manager

from django_framework.django_helpers.model_helpers.model_registry import get_model

class JobManager(BaseManager):
    Model = get_model(model_name = 'Job')


    @classmethod
    def _relationship_name_format(cls, relationship_name=None, relationship_list=None):
        if relationship_name == 'profile':
            query_key = cls.NO_PROFILE_RELATIONSHIP_FILTER
        return query_key, relationship_list
    
    
    @classmethod
    def _get_related_model(cls, models, relationship_name):
#         '''This method allows us to the related profile mainly for invalidating caches!  it might be useful for other things...'''
        if relationship_name == 'profile':
            return cls.NO_RELATED_PROFILES
            
    

register_manager(JobManager)
