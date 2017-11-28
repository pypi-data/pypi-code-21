
from api import api_models, api_model
from django_framework.django_helpers.url_helpers.regex_url import MacroUrlPattern
from django_framework.django_helpers.exception_helpers import try_except_channels
from django_framework.django_helpers.channel_helpers.message_formatter import message_formatter

@message_formatter
@try_except_channels
def ws_models(request, model_name_slug=None):
    response = api_models(request=request, model_name_slug=model_name_slug)
    return response


@message_formatter
@try_except_channels
def ws_model(request, model_name_slug=None, model_pk = None, model_uuid=None):
    response = api_model(request = request, model_name_slug = model_name_slug, model_pk = model_pk, model_uuid = model_uuid)
    return response

@message_formatter
@try_except_channels
def ws_admin_models(request, model_name_slug=None):
    response = api_models(request=request, model_name_slug=model_name_slug, admin = True)
    return response

@message_formatter
@try_except_channels
def ws_admin_model(request, model_name_slug=None, model_pk = None, model_uuid=None):
#     raise LoginError(message = 'woops', notes = 'hey this is a test', http_status = 404, error_code = 4040)
    response = api_model(request = request, model_name_slug = model_name_slug, model_pk = model_pk, model_uuid = model_uuid, admin = True)
    return response


routes = [
        ("http_request.json", ws_models, {'path' : MacroUrlPattern(':model_name_slug/models/$').compiled}),
        ("http_request.json", ws_model, {'path' :  MacroUrlPattern(':model_name_slug/models/:model_uuid/$').compiled}),
        ("http_request.json", ws_model, {'path' :  MacroUrlPattern(':model_name_slug/models/:model_pk/$').compiled}),
        
        ("http_request.json", ws_admin_models, {'path' : MacroUrlPattern('admin/:model_name_slug/models/$').compiled}),
        ("http_request.json", ws_admin_model, {'path' :  MacroUrlPattern('admin/:model_name_slug/models/:model_uuid/$').compiled}),
        ("http_request.json", ws_admin_model, {'path' :  MacroUrlPattern('admin/:model_name_slug/models/:model_pk/$').compiled}),
]