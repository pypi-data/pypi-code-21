
from django_framework.django_helpers.channel_helpers.message_formatter import message_formatter


from api import api_model_jobs, api_model_job, api_admin_model_jobs, api_admin_model_job


from django_framework.django_helpers.url_helpers.regex_url import MacroUrlPattern
from django_framework.django_helpers.exception_helpers import try_except_channels

@message_formatter
@try_except_channels
def ws_model_jobs(request, model_name_slug, model_pk = None, model_uuid = None):
    response = api_model_jobs(request, model_name_slug, model_pk = model_pk, model_uuid = model_uuid)
    return response


@message_formatter
@try_except_channels
def ws_model_job(request, model_name_slug, model_pk = None, model_uuid = None, job_uuid = None):
    response = api_model_job(request, model_name_slug=model_name_slug, model_pk = model_pk, model_uuid = model_uuid, job_uuid = job_uuid)
    return response


@message_formatter
@try_except_channels
def ws_admin_model_jobs(request, model_name_slug, model_pk = None, model_uuid = None):
    response = api_admin_model_jobs(request, model_name_slug, model_pk = model_pk, model_uuid = model_uuid, admin = True, )
    return response


@message_formatter
@try_except_channels
def ws_admin_model_job(request, model_name_slug, model_pk = None, model_uuid = None, job_uuid = None, admin = True):
    response = api_admin_model_job(request, model_name_slug=model_name_slug, model_pk = model_pk, model_uuid = model_uuid, job_uuid = job_uuid)
    return response


routes = [
        ("http_request.json", ws_model_jobs, {'path' : MacroUrlPattern(':model_name_slug/models/:model_uuid/job/$').compiled}),
        ("http_request.json", ws_model_jobs, {'path' :  MacroUrlPattern(':model_name_slug/models/:model_pk/job/$').compiled}),
        ("http_request.json", ws_model_job, {'path' :  MacroUrlPattern(':model_name_slug/models/:model_uuid/job/:job_uuid/$').compiled}),
        ("http_request.json", ws_model_job, {'path' :  MacroUrlPattern(':model_name_slug/models/:model_pk/job/:job_uuid/$').compiled}),
        
        ("http_request.json", ws_admin_model_jobs, {'path' : MacroUrlPattern('admin/:model_name_slug/models/:model_uuid/job/$').compiled}),
        ("http_request.json", ws_admin_model_jobs, {'path' : MacroUrlPattern('admin/:model_name_slug/models/:model_pk/job/$').compiled}),
        ("http_request.json", ws_admin_model_job, {'path' :  MacroUrlPattern('admin/:model_name_slug/models/:model_uuid/job/:job_uuid/$').compiled}),
        ("http_request.json", ws_admin_model_job, {'path' :  MacroUrlPattern('admin/:model_name_slug/models/:model_pk/job/:job_uuid/$').compiled}),
]