from django.apps import AppConfig
from django.core.handlers.wsgi import WSGIHandler

from .http.request import ExtendedWSGIRequest


class DjangoExtendedJsonConfig(AppConfig):
    name = 'djext.json'
    verbose_name = 'JSON tools'

    def ready(self):
        WSGIHandler.request_class = ExtendedWSGIRequest
