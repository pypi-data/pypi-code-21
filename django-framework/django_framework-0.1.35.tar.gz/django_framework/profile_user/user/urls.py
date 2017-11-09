from django.conf.urls import url
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from django_framework.django_helpers.url_helpers import regex_url
from api import UserAPI

from django_framework.django_helpers.exception_helpers import try_except_response

@api_view(["POST"])
@try_except_response
def register(request, model_name=None):
    api = UserAPI(model_name = model_name, request = request)
    api.register()
    response = api.get_response()
    
    http_response = Response(response, status = 200)
    if True: # this sets a cookie which can also be used!
        http_response.set_cookie(key = 'AUTHORIZATIONID', value=response['data'][0]['token'], max_age = 86400)
    return http_response

@api_view(["POST"])
@try_except_response
def login(request, model_name=None):
    api = UserAPI(model_name = model_name, request = request)
    user = api.login()
    response = api.get_response()
    
    
    http_response = Response(response, status = 200)
    if True: # this sets a cookie which can also be used!
        http_response.set_cookie(key = 'AUTHORIZATIONID', value=response['data'][0]['token'], max_age = 86400)
    return http_response

@api_view(["GET", "PUT", "POST"])
@try_except_response
def logout(request, model_name=None):
    api = UserAPI(model_name = model_name, request = request)
    api.logout()
    response = api.get_response()

    http_response = Response(response, status = 200)
    http_response.set_cookie(key = 'AUTHORIZATIONID', value=None, max_age = 1)  # wipe cookie!
    return http_response

@api_view(["GET"])
@try_except_response
def default_login(request, model_name=None):
    api = UserAPI(model_name = model_name, request = request)
    user = api.default_login()
    response = api.get_response()
    
    
    http_response = Response(response, status = 200)
    if True: # this sets a cookie which can also be used!
        http_response.set_cookie(key = 'AUTHORIZATIONID', value=response['data'][0]['token'], max_age = 86400)
    return http_response


urlpatterns = [
    regex_url.url(r'^register/$', register),
    regex_url.url(r'^login/$', login),
    regex_url.url(r'^logout/$', logout),
    regex_url.url(r'^login2/$', default_login),
]