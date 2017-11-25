from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import WSGIHandler, WSGIRequest


class DjangoExtendedHttpConfig(AppConfig):
    name = 'djext.http'
    verbose_name = 'HTTP tools'

    def ready(self):
        WSGIHandler.request_class = self.get_request_class()

    def get_request_class(self):
        request_class = None
        custom_request_class = getattr(settings, 'DJEXT_REQUEST_CLASS', 'djext.http.wsgi.ExtendedWSGIRequest')
        if custom_request_class and '.' in custom_request_class:
            module_name, class_name = custom_request_class.rsplit('.', 1)
            module = __import__(module_name, fromlist=[class_name])
            request_class = getattr(module, class_name)
        if not issubclass(request_class, WSGIRequest):
            raise ImproperlyConfigured('The custom request class must extend the generic WSGIRequest')
        return request_class
