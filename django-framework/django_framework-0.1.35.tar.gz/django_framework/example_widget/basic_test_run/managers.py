
from django_framework.django_helpers.manager_helpers.base_manager import BaseManager

from django_framework.django_helpers.manager_helpers.manager_registry import register_manager, get_manager

from django_framework.django_helpers.model_helpers.model_registry import get_model

class BasicTestRunManager(BaseManager):
    Model = get_model(model_name = 'BasicTestRun')

    @classmethod
    def _relationship_name_format(cls, relationship_name=None, relationship_list=None):
        if relationship_name == 'profile':
            query_key = 'id__in'
            query_key = 'pass' # skip over it
        return query_key, relationship_list
    
    
    @classmethod
    def _get_related_model(cls, models, relationship_name):
        '''This method allows us to the related profile mainly for invalidating caches!  it might be useful for other things...'''
        if relationship_name == 'profile':
            
#             user_ids = [model.user.id for model in models]
            ProfileManager = get_manager(manager_name = 'profile')
            models = ProfileManager.get_by_query(query_params = {})
            
            
            return models
        else:
            raise ValueError('The relationship name requested was not understood')

        return models


register_manager(BasicTestRunManager)
