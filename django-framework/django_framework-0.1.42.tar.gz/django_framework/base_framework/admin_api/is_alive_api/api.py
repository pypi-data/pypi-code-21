
import copy
from django_framework.django_helpers.api_helpers import BaseAPI
from django.conf.urls import RegexURLPattern, RegexURLResolver
from django.core import urlresolvers

from django_framework.django_helpers.model_helpers.model_registry import get_model, get_model_name_list
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer
from django_framework.django_helpers.manager_helpers.manager_registry import get_manager
from django_framework.django_helpers.meta_helpers.meta_registry import get_meta


# the easiest thing to do is to get all the models!
from django.conf import settings
class ProfileAPI(BaseAPI):
    # each server MUST have a way of "deleting all entries associated with a given profile...
    # if delete is impossible then it should render information irretrievable"
    def __init__(self, request, admin = False, **kwargs):
        
        kwargs['is_authenticated'] = False # we want to check later!
        super(DocumentationAPI, self).__init__(request=request, **kwargs)


    def server_endpoints(self):
        
        endpoints = {}
        endpoints['base_url'] = settings.SERVER_URL
        endpoints['server_group'] = settings.SERVER_GROUP
        endpoints['server_name'] = settings.SERVER_NAME
        
        endpoints['models'] = [x.lower() for x in get_model_name_list()]
        endpoints['urls'] = self.get_resolved_urls()
        
        
        self.response = endpoints
        return endpoints
    
    def get_resolved_urls(self):
        urls = urlresolvers.get_resolver()
        all_urls = list()

        def func_for_sorting(i):
            if i.name is None:
                i.name = ''
            return i.name

        def show_urls(urls):
            for url in urls.url_patterns:
                if isinstance(url, RegexURLResolver):
                    show_urls(url)
                elif isinstance(url, RegexURLPattern):

                    if url.name not in ['models', 'models_jobs', 'docs', 'ignore', 'render_panel','sql_select', 'sql_explain', 'sql_profile', 'template_source']:
                        all_urls.append(url.regex.pattern)
        show_urls(urls)
        
        return all_urls
    
    
    def get_response(self):
        '''Override BaseAPI version of get_response to get autoformatting of data'''
        return self.format_data(data = self.response)
    
    def format_data(self, data):

        return dict(data=data, meta_data = {'type' : 'docs', "total_query_results": 1})
    
    
    def check_allowed_method(self):
        pass
    