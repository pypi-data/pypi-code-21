from rest_framework.response import Response
from rest_framework.decorators import api_view

from django_framework.django_helpers.url_helpers import regex_url
from django_framework.django_helpers.exception_helpers import try_except_response

from api import api_model_jobs, api_model_job, api_admin_model_jobs, api_admin_model_job


@api_view(["GET", "POST"])
@try_except_response
def url_model_jobs(request, model_name_slug, model_pk = None, model_uuid = None):
    response = api_model_jobs(request, model_name_slug, model_pk = model_pk, model_uuid = model_uuid)
    return Response(response, status = 200)


@api_view(["GET", "PUT", "DELETE"])
@try_except_response
def url_model_job(request, model_name_slug, model_pk = None, model_uuid = None, job_uuid = None):
    response = api_model_job(request, model_name_slug=model_name_slug, model_pk = model_pk, model_uuid = model_uuid, job_uuid = job_uuid)
    return Response(response, status = 200)


@api_view(["GET", "POST"])
@try_except_response
def url_admin_model_jobs(request, model_name_slug, model_pk = None, model_uuid = None):
    response = api_admin_model_jobs(request, model_name_slug, model_pk = model_pk, model_uuid = model_uuid, admin = True, )
    return Response(response, status = 200)


@api_view(["GET", "PUT", "DELETE"])
@try_except_response
def url_admin_model_job(request, model_name_slug, model_pk = None, model_uuid = None, job_uuid = None, admin = True):
    response = api_admin_model_job(request, model_name_slug=model_name_slug, model_pk = model_pk, model_uuid = model_uuid, job_uuid = job_uuid)
    return Response(response, status = 200)



urlpatterns = [

    regex_url.url(':model_name_slug/models/:model_uuid/job/$', url_model_jobs, name = 'models_jobs'),
    regex_url.url(':model_name_slug/models/:model_pk/job/$', url_model_jobs, name = 'models_jobs'),
    regex_url.url(':model_name_slug/models/:model_uuid/job/:job_uuid/$', url_model_job, name = 'models_jobs'),
    regex_url.url(':model_name_slug/models/:model_pk/job/:job_uuid/$', url_model_job, name = 'models_jobs'),


    regex_url.url('admin/:model_name_slug/models/:model_uuid/job/$', url_admin_model_jobs, name = 'models_jobs'),
    regex_url.url('admin/:model_name_slug/models/:model_pk/job/$', url_admin_model_jobs, name = 'models_jobs'),
    regex_url.url('admin/:model_name_slug/models/:model_uuid/job/:job_uuid/$', url_admin_model_job, name = 'models_jobs'),
    regex_url.url('admin/:model_name_slug/models/:model_pk/job/:job_uuid/$', url_admin_model_job, name = 'models_jobs'),
]