from django.apps import AppConfig
from django.core.handlers.wsgi import WSGIHandler

from .http.request import ExtendedWSGIRequest


class DjangoExtendedConfig(AppConfig):
    name = 'djext'
    verbose_name = 'Quick tools for Django'

    def ready(self):
        WSGIHandler.request_class = ExtendedWSGIRequest
