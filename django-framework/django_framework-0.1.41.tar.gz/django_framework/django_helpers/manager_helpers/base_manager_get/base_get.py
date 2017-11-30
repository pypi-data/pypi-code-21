import arrow
import operator
from inflector import Inflector
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db.models import QuerySet, ManyToManyField, Q, F
from django.core.exceptions import ObjectDoesNotExist

from functools import wraps


class BaseManagerGet(object):
    '''There are some wierd nuances when filtering and doing things with M2M fields'''
    
    DICTIONARY_TYPE_FILTERS = ["exclude", "filter", "exclude", "annotate"]
    LIST_TYPE_FILTERS = ["distinct", "order_by", "q_or", "select_related"]


    @classmethod
    def get_by_query(cls, query_params=None, query_set = None):
        cls.check_class_attributes_are_set()
        if query_params is None:
            query_params = {}
            
        if not isinstance(query_params, dict):
            raise TypeError("query_params must be a dict.")

#         cls.set_distinct_params(query_params)  # we are not allowed to distinct using mysql
        
        if query_set == None:
            query_set = cls.Model.objects.all() # <--- minus this!
        
        cls.check_class_attributes_are_set()
        
        
        if query_params.get('relationship'):
            # this modifies anything as a "relationship" into the proper lookups -- mainly used by permissions
            query_params = cls._relationship_by_query(query_params=query_params)
            
            
        for allowed_query_param in ["select_related", "q_or", "filter", "exclude", "order_by", "distinct",]: # this needs to be ordered to run specifically in this way!
            if query_params.get(allowed_query_param):

                cls._validate_query_request(
                    param_name=allowed_query_param, params=query_params[allowed_query_param], query_set=query_set)
                
                
                method = getattr(cls, '_' + allowed_query_param + '_by_query')
                query_set = method(query_params[allowed_query_param], query_set=query_set)
# 


#         if query_params.get("select_related"):
#             query_set = cls._select_related_by_query(
#                 select_related_params=query_params["select_related"], query_set=query_set
#             )
#         if query_params.get("q_or"):
#             query_set = cls._q_or_by_query(
#                 q_or_params=query_params["q_or"], query_set=query_set
#             )
#         if query_params.get("filter"):
#             query_set = cls._filter_by_query(
#                 filter_params=query_params["filter"], query_set=query_set
#             )
#         if query_params.get("exclude"):
#             query_set = cls._exclude_by_query(
#                 exclude_params=query_params["exclude"], query_set=query_set
#             )
#         if query_params.get("order_by"):
#             query_set = cls._order_by_query(
#                 order_by_params=query_params["order_by"], query_set=query_set
#             )
#         if isinstance(query_params.get("distinct"), list):
#             query_set = cls._distinct_by_query(
#                 distinct_params=query_params["distinct"], query_set=query_set
#             )
        return query_set


    @classmethod
    def set_distinct_params(cls, query_params):
        if query_params.get("distinct") is None and not query_params.get("order_by"):
            query_params["distinct"] = ["id"]
        elif not query_params.get("order_by") and isinstance(query_params.get("distinct"), list):
            if len(query_params["distinct"]) == 0:
                query_params["distinct"].append("id")

    @classmethod
    def _validate_query_request(cls, param_name, params, query_set):
        if param_name in cls.DICTIONARY_TYPE_FILTERS and not isinstance(params, dict):
            error_message = "Your {param_name} params are structured incorrectly.  It should be a dict."
            raise TypeError(error_message.format(param_name=param_name))
        elif param_name in cls.LIST_TYPE_FILTERS and not isinstance(params, list):
            error_message = "Your {param_name} params are structured incorrectly it should be a list."
            raise TypeError(error_message.format(param_name=param_name))

        if not isinstance(query_set, QuerySet):
            raise TypeError("The query_set provided must be a Django Queryset")

    # currently inaccessible because of permissions issues # i wonder what you mean by this but whatevs
    @classmethod
    def _annotate_by_query(cls, annotate_params, query_set=None):
        
        annotate_query = {k: F(v) for k, v in annotate_params.items()}
        response = query_set.annotate(**annotate_query)
        return response

    @classmethod
    def _select_related_by_query(cls, select_related_params, query_set=None):
        return query_set.select_related(*select_related_params)

    @classmethod
    def _q_or_by_query(cls, q_or_params, query_set=None):
        q_list = [Q(**query) for query in q_or_params]
        response = query_set.filter(reduce(operator.or_, q_list))
        return response

    @classmethod
    def _filter_by_query(cls, filter_params, query_set=None):
        response = query_set.filter(**filter_params)
        return response

    @classmethod
    def _exclude_by_query(cls, exclude_params, query_set=None):
        response = query_set.exclude(**exclude_params)
        return response

    @classmethod
    def _order_by_by_query(cls, order_by_params, query_set=None):
        '''The wierd name is to match conventions.'''

        response = query_set.order_by(*order_by_params)
        return response

    @classmethod
    def _distinct_by_query(cls, distinct_params, query_set=None):
        response = query_set.distinct(*distinct_params)
        return response


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
    def _relationship_name_format(cls, relationship_name=None, relationship_list=None):
        raise NotImplementedError('Please implement a model specific version to limit by logged in user!')



    @classmethod
    def _relationship_by_query(cls, query_params):
        # for filtering by distant/unclear relationships
        # query_params {'relationship' : {<relationship_name> : <relationship_list_of_ids>}}
        relationships = query_params.pop('relationship', {})
        
        for relationship_name, relationship_list in relationships.items():
            relationship_name = relationship_name.lower()
        
            
            query_key, relationship_list = cls._relationship_name_format(relationship_name = relationship_name, relationship_list = relationship_list)
            if query_key == None:
                message = "We can't get {model_name} models through a {relationship_name} relationship."
                raise NotImplementedError(message.format(model_name='Poll',
                                                         relationship_name=relationship_name))
            
            if query_key != 'pass': # special key word to skip adding in the relationship
                query_params = cls._update_query_relationship(query_params=query_params, relationship_name=query_key, relationship_list=relationship_list)
        
        return query_params
    
    
    @classmethod
    def get_related_model(cls, models, relationship_name):
        
        '''For this one, it's for the given models, give me the models that are associated to it via the relationship!
        The thing that breaks design patterns for this is that it returns a differnt model eachtime!
        this is needed for mapping things back to profile so we can invalidate caches and what not.
        '''
        return cls._get_related_model(models = models, relationship_name = relationship_name)
    
    