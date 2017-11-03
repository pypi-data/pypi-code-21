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


from api import api_models, api_model

from django_framework.django_helpers.exception_helpers import try_except_response


@api_view(["GET", "POST"])
@try_except_response
def url_models(request, model_name_slug):
    response = api_models(request=request, model_name_slug=model_name_slug)
    return Response(response, status = 200)


@api_view(["GET", "PUT", "DELETE"])
@try_except_response
def url_model(request, model_name_slug, model_pk = None, model_uuid=None):
    response = api_model(request = request, model_name_slug = model_name_slug, model_pk = model_pk, model_uuid = model_uuid)
    return Response(response, status = 200)


@api_view(["GET", "POST"])
@try_except_response
def url_admin_models(request, model_name_slug):
    response = api_models(request=request, model_name_slug=model_name_slug, admin = True)
    return Response(response, status = 200)


@api_view(["GET", "PUT", "DELETE"])
@try_except_response
def url_admin_model(request, model_name_slug, model_pk = None, model_uuid=None):
    response = api_model(request = request, model_name_slug = model_name_slug, model_pk = model_pk, model_uuid = model_uuid, admin = True)
    return Response(response, status = 200)


urlpatterns = [
    regex_url.url(':model_name_slug/models/$', url_models, name = 'models'),
    regex_url.url(':model_name_slug/models/:model_uuid/$', url_model, name = 'models'),
    regex_url.url(':model_name_slug/models/:model_pk/$', url_model, name = 'models'),

    regex_url.url('admin/:model_name_slug/models/$', url_admin_models, name = 'models'),
    regex_url.url('admin/:model_name_slug/models/:model_uuid/$', url_admin_model, name = 'models'),
    regex_url.url('admin/:model_name_slug/models/:model_pk/$', url_admin_model, name = 'models'),
]