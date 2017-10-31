from django.conf.urls import url
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
# from app_apis import get_api
# from app_models import get_model
# from django_framework.helpers._exceptions import try_except_response, PermissionError
# from django_framework.helpers.service_helpers import is_correct_service, service_redirect
# from django_framework.helpers.cache_helpers import get_model_request_cache_value

from django_framework.django_helpers.exception_helpers import try_except_response
from django_framework.django_helpers.url_helpers import regex_url


# from api import BasicTestRunAPI
# 
@api_view(["GET"])
@try_except_response
def raise_error(request, model_name=None):
    raise Exception('Testing Errors!')
    return Response(response, status = 200)
# 
# 
urlpatterns = [
    regex_url.url('testing/raise_error/$', raise_error, name = 'example'),
]