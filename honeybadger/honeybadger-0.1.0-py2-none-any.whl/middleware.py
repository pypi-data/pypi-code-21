from honeybadger import honeybadger
from six import iteritems

try:
    # Support for Django 1.10...
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # ...while maintaining support for Django <= 1.9.
    class MiddlewareMixin(object):
        def __init__(self, get_response=None):
            pass

class DjangoHoneybadgerMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super(DjangoHoneybadgerMiddleware, self).__init__(get_response=get_response)
        from django.conf import settings
        if getattr(settings, 'DEBUG'):
            honeybadger.configure(environment='development')
        config_kwargs = dict([(k.lower(), v) for (k, v) in iteritems(getattr(settings, 'HONEYBADGER', {}))])
        honeybadger.configure(**config_kwargs)
        honeybadger.config.set_12factor_config() # environment should override Django settings

    def process_request(self, request):
        honeybadger.begin_request(request)
        return None

    def process_exception(self, request, exception):
        honeybadger.notify(exception)
        return None

    def process_response(self, request, response):
        honeybadger.reset_context()
        return response

# TODO: finish Flask support
class FlaskHoneybadgerMiddleware(object):
    def __init__(self, app, **kwargs):
        raise NotImplemented
        # return app
