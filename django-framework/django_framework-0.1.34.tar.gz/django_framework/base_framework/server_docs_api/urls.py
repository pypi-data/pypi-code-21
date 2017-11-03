from django.conf.urls import url
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
# from app_apis import get_api
# from app_models import get_model
# from django_framework.helpers._exceptions import try_except_response, PermissionError
# from django_framework.helpers.service_helpers import is_correct_service, service_redirect
# from django_framework.helpers.cache_helpers import get_model_request_cache_value


from django_framework.django_helpers.url_helpers import regex_url

from api import DocumentationAPI
from model_docs import ModelDocAPI

from django_framework.django_helpers.exception_helpers import try_except_response

@api_view(["GET"])
@try_except_response
def doc_endpoints(request):
    '''The goal of this endpoint is to determine what is being served by this erver,
    # in particular, the models, and any specia "endpoints.  This is useful for routing purposes!'''
    
    dapi = DocumentationAPI(request = request)
    dapi.server_endpoints()
    
    response = dapi.get_response()
    
    return Response(response)

@api_view(["GET"])
@try_except_response
def model_doc_endpoints(request, model_name_slug = None):
    '''The goal of this endpoint is to determine what is being served by this erver,
    # in particular, the models, and any specia "endpoints.  This is useful for routing purposes!'''
    
    dapi = ModelDocAPI(request = request, model_name = model_name_slug)
    dapi.get_model_docs()
    
    response = dapi.get_response()
    
    return Response(response)

@api_view(["GET"])
@try_except_response
def admin_model_doc_endpoints(request, model_name_slug = None):
    '''The goal of this endpoint is to determine what is being served by this erver,
    # in particular, the models, and any specia "endpoints.  This is useful for routing purposes!'''
    
    dapi = ModelDocAPI(request = request, model_name = model_name_slug, admin = True)
    dapi.get_model_docs()
    
    response = dapi.get_response()
    
    return Response(response)

urlpatterns = [

    regex_url.url('docs/endpoints/$', doc_endpoints, name = 'docs'),
    
    regex_url.url(':model_name_slug/docs/$', model_doc_endpoints, name = 'docs'),
    regex_url.url('admin/:model_name_slug/docs/$', admin_model_doc_endpoints, name = 'docs'),
]