from django.conf.urls import url,RegexURLResolver,RegexURLPattern
from rest_framework_swagger.views import get_swagger_view
from django import conf
from django.conf import settings
from django.core.checks.urls import check_resolver
from django.core.checks.registry import register,Tags
import django.core.checks.urls


schema_view = get_swagger_view(title='Pastebin API')

conf.settings.INSTALLED_APPS.append('rest_framework_swagger')
swagger_regex = RegexURLPattern('^swagger-ui.html$',schema_view)

@register(Tags.urls)
def check_url_config(app_configs, **kwargs):
    if getattr(settings, 'ROOT_URLCONF', None):
        from django.urls import get_resolver
        resolver = get_resolver()
        global swagger_regex
        resolver.url_patterns.append(swagger_regex)
        return check_resolver(resolver)
    return []

django.core.checks.urls.check_url_config = check_url_config


import coreapi
from coreapi.compat import force_bytes
from openapi_codec import OpenAPICodec as _OpenAPICodec
from openapi_codec.encode import generate_swagger_object
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework import status
import simplejson as json
from rest_framework_swagger.settings import swagger_settings
class OpenAPICodec(_OpenAPICodec):
    def encode(self, document, extra=None, **options):
        if not isinstance(document, coreapi.Document):
            raise TypeError('Expected a `coreapi.Document` instance')

        data = generate_swagger_object(document)
        if isinstance(extra, dict):
            data.update(extra)

        return force_bytes(json.dumps(data))

class OpenAPIRenderer(BaseRenderer):
    media_type = 'application/openapi+json'
    charset = None
    format = 'openapi'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context['response'].status_code != status.HTTP_200_OK:
            return JSONRenderer().render(data)
        extra = self.get_customizations()

        return OpenAPICodec().encode(data['data'], extra=extra)

    def get_customizations(self):
        """
        Adds settings, overrides, etc. to the specification.
        """
        data = {}
        if swagger_settings.SECURITY_DEFINITIONS:
            data['securityDefinitions'] = swagger_settings.SECURITY_DEFINITIONS

        return data

import rest_framework_swagger.renderers
rest_framework_swagger.renderers.OpenAPIRenderer = OpenAPIRenderer
