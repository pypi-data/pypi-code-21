import operator
from inflector import Inflector
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db.models import QuerySet, ManyToManyField, Q, F
from django.core.exceptions import ObjectDoesNotExist
# from app_models import get_model_name
# from app_serializers import get_serializer_name
# from django_framework.helpers.time_helpers import now
# from django_framework.helpers.cache_helpers import invalidate_model_cache

from django_framework.django_helpers.cache_helpers import ManagerCache, APICache
import collections



from django.conf import settings
import arrow
import copy


from base_manager_get import BaseManagerGet


from django_framework.django_helpers.model_helpers.model_registry import get_model_name
from __builtin__ import classmethod

class BaseManager(BaseManagerGet):
    Model = None

    NO_RELATED_PROFILES = [] # a constant to hold the proper value when there are no related profiles
    NO_PROFILE_RELATIONSHIP_FILTER = 'pass' # a constant to hold the proper value when there are no profiles to filter by


    @classmethod
    def validate(cls, Serializer=None, data=None, model = None):
        '''To the best of our abilities, verifies that the create/update is valid!'''
        cls.check_class_attributes_are_set()
        cls.check_serializer_class(serializer=Serializer)
        if data is None:
            data = {}
        if model == None:
            serializer = Serializer(data=data, partial = True)
        else:
            serializer = Serializer(model, data=data, partial=True)
            
        if serializer.is_valid(raise_exception=True):
            return serializer
        else:
            return False
            

    @classmethod
    def create(cls, Serializer=None, data=None, clear_cache=True):
#         settings.KAFKA_PRODUCER.send('global', {'something': 'creating something!'})

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
            for field_name in validated_data.keys():
                field = cls.Model._meta.get_field(field_name)
                
                if isinstance(field, ManyToManyField): # or ArrayField, or JSONField
                    validated_data_clean.pop(field_name)
            
            obj = cls.Model.objects.create(**validated_data_clean)  # you cant update many to many like this...
            
            if validated_data_clean != validated_data:
                obj = cls._update_model(obj, validated_data=validated_data)
#

            if clear_cache:
                cls._clear_cache(models = [obj])

            return [obj]

    @classmethod
    def update(cls, Serializer=None, data=None, model = None, clear_cache=True):
        cls.check_class_attributes_are_set()
        cls.check_serializer_class(serializer=Serializer)
        
        if model is None:
            raise ValueError('You cannot attempt to update something that is None')
        
        serializer = cls.validate(Serializer=Serializer, data=data, model = model)
        if serializer:
            validated_data = serializer.validated_data
            model = cls._update_model(model, validated_data)

            if clear_cache:
                cls._clear_cache(models = [model])

            return [model]
        raise ValueError('You have a reached a part of code that you should never have ever reached.  Base Manager Update')

    @classmethod
    def _update_model(cls, model, validated_data=None):
        
        if isinstance(validated_data, dict):
            for field_name in validated_data.keys():
                field = cls.Model._meta.get_field(field_name)

                if isinstance(field, ManyToManyField):
                    cls._update_model_many_to_many_field(model_field = getattr(model, field_name), field_value = validated_data[field_name])
                elif isinstance(field, ArrayField):
                    setattr(
                        model, field_name,
                        cls._update_model_array_field(model_field = getattr(model, field_name), field_value = validated_data[field_name])
                    )
                else:
                    setattr(model, field_name, validated_data[field_name])
#                     raise ValueError("`{}` cannot be updated in this way.".format(field_name))
        model.save()
        return model


    @classmethod
    def _update_model_many_to_many_field(cls, model_field, field_value):
        if isinstance(field_value, dict):
            if field_value["update_action"] == "add":
                model_field.add(*field_value.get("data", []))
            if field_value["update_action"] == "remove":
                model_field.remove(*field_value.get("data", []))
            if field_value["update_action"] == "set":
                model_field.set(field_value.get("data", []))
            if field_value["update_action"] == "clear":
                model_field.clear()
        else:
            model_field.add(*field_value)

        return model_field


    @classmethod
    def _update_model_array_field(cls, current_value, field_value):
        if isinstance(field_value, dict):
            if field_value["update_action"] == "add":
                if current_value is None:
                    current_value = []
                current_value += field_value.get("data", [])
            if field_value["update_action"] == "remove" and current_value is not None:
                current_value = [v for v in current_value if v not in field_value.get("data", [])]
            if field_value["update_action"] == "set":
                if current_value is None:
                    current_value = []
                current_value += field_value.get("data", [])
            if field_value["update_action"] == "clear":
                current_value = []
        else:
            current_value = field_value
            
            
    @classmethod
    def _get_models(cls, query_params=None, models=None):
        if query_params is not None and models is not None:
            raise ValueError("Requires either `query_params` or `models`, not both")

        if models is not None:
            if models is not None and not (isinstance(models, list), isinstance(models, QuerySet)):
                raise ValueError("`models` must be a list or QuerySet.")
            if models:
                for model in models:
                    if not isinstance(model, cls.Model):
                        raise TypeError(
                            "model in `models` must be a {} instance.".format(str(cls.Model))
                        )
        else:
            models = cls.get_by_query(query_params=query_params)

        if len(models) > 1:
            error_message = "Currently there is no support for updating multiple with one request"
            raise NotImplementedError(error_message)
        elif len(models) < 1:
            error_message = "Could not find the model to update."
            raise ObjectDoesNotExist(error_message)

        return models

    @classmethod
    def delete(cls, model=None, query_params=None, clear_cache=True):
        cls.check_class_attributes_are_set()
        
        if model == None:
            if not query_params:
                raise ValueError("Safety precaution, please specify what you are deleting.")
            instances = cls.get_by_query(query_params=query_params)
            if len(instances) > 1:
                raise ValueError("Safety precaution, you may only delete one record at a time.")
            elif len(instances) == 1:
                instances.delete()
                return [{"status" : True}]
        else:
            if (type(model) == list or type(model) == QuerySet):
                if len(model) != 1:
                    raise ValueError('Saftey precaution, you have 0 or 2+ record at a time!')
                model = model[0]
            model.delete()

        return [{"status" : True}]

    @classmethod
    def check_class_attributes_are_set(cls):
        if cls.Model is None:
            error_message = "This manager's Model has not been set"
            raise AttributeError(error_message)
        else:
            return True

    @classmethod
    def check_serializer_class(cls, serializer=None):
        
        if serializer.Meta.model != cls.Model:
            error_message = "The Serializer provided is invalid for this Manager."
            raise TypeError(error_message)

    @classmethod
    def _update_query(cls, query_params, param_name, update_dict):
        if param_name not in query_params:
            query_params[param_name] = {}

        query_params[param_name].update(**update_dict) # this means that if there is an existing key, it will override it!
        # which in most cases is pretty reasonable....
        return query_params


    @classmethod
    def _update_query_relationship(cls, query_params, relationship_name, relationship_list):

        try:
            original_value = query_params['filter'][relationship_name] # it can be: str, int, float, list
            if not(isinstance(original_value, collections.Sequence) and not isinstance(original_value, basestring)):
                # it is probably not a list!
                original_value = list(original_value) # conver to a list
                
            # we want to do this anyway!
            new_value = set(original_value) & set(relationship_list)
                
        except:
            new_value = relationship_list
        
        query_params = cls._update_query(query_params = query_params, param_name = "filter", update_dict = {relationship_name : new_value})
        return query_params

    @classmethod
    def send_job(cls, model, command, action):
        worker = model.get_worker()
        job = worker.create_job(data=dict(command=command, action=action))[0]
        return worker.send_job(job=job)


    @classmethod
    def get_cache(cls, key):
        return ManagerCache(model_name = cls.Model.__name__, key = key)
    
    
    @classmethod
    def _clear_cache(cls, models):
        
        profile_models = cls.get_related_model(models = models, relationship_name = 'profile')
        
        full_name, model_name = get_model_name(cls.Model)
        if len(profile_models) > 10:
            api_cache = APICache(model_name = model_name, token = None, url = '')
            api_cache.clear_level(level = 2, token = None)
        else:
            
            for profile in profile_models:
                api_cache = APICache(model_name = model_name, token = profile.uuid, url = '')
                response = api_cache.clear_level(level = 1, token = profile.uuid)

    
    
    @classmethod
    def create_or_update(cls, Serializer, query_params, data, clear_cache = True):
        
        objs = cls.get_by_query(query_params = query_params)
        
        if len(objs) == 0:
            objs = cls.create(Serializer = Serializer, data = data, clear_cache = clear_cache)
            
        else:
            objs = cls.update(Serializer = Serializer, data = data, model = objs[0], clear_cache = clear_cache)
        
        
        return objs
        
        