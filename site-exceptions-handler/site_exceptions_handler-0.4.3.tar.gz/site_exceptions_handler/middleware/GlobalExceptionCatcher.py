from __future__ import absolute_import, unicode_literals

import datetime
import logging
import sys
import uuid
import django

from django import http
from django.conf import settings
from django.core.urlresolvers import RegexURLResolver
from django.template import Context, Template
from django.views.debug import ExceptionReporter

from site_exceptions_handler import TECHNICAL_500_TEMPLATE, TECHNICAL_500_TEXT_TEMPLATE
from site_exceptions_handler.models import SiteExceptionLogger, SiteExceptionLoggerTally

logger = logging.getLogger('server_exception_logging')


if django.VERSION >= (1, 10):
    from django.utils.deprecation import MiddlewareMixin
else:
    MiddlewareMixin = object


def resolver(request):
    """
    Returns a RegexURLResolver for the request's urlconf.

    If the request does not have a urlconf object, then the default of
    settings.ROOT_URLCONF is used.
    """
    from django.conf import settings
    urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
    return RegexURLResolver(r'^/', urlconf)


# class StandardExceptionMiddleware(object):
class StandardExceptionMiddleware(MiddlewareMixin):
    """

    TAKEN FROM https://djangosnippets.org/snippets/638/

    DO NOT USE: `class StandardExceptionMiddleware(object):`
     will result in TypeError: object() takes no parameters
     As of 1.10 yu will need to process with the `MiddlewareMixin`
     else you could use this methoid:

     ```
        class StandardExceptionMiddleware(object):
            def __init__(self, get_response):
              self.get_response = get_response

            def __call__(self, request):
              return self.get_response(request)

    ```

    """

    def process_exception(self, request, exception):
        # Get the exception info now, in case another exception is thrown later.
        if isinstance(exception, http.Http404):
            return self.handle_404(request, exception)
        else:
            return self.handle_error(request, exception)

    def handle_404(self, request, exception):
        pass

    def handle_error(self, request, exception):
        exc_info = sys.exc_info()
        if settings.DEBUG:
            self.store_exception(request, exception, exc_info)
            self.log_exception(request, exception, exc_info)
            return self.debug_500_response(request, exception, exc_info)
        else:
            self.store_exception(request, exception, exc_info)
            self.log_exception(request, exception, exc_info)
            return self.production_500_response(request, exception, exc_info)

    def debug_500_response(self, request, exception, exc_info):
        from django.views import debug
        return debug.technical_500_response(request, *exc_info)

    def production_500_response(self, request, exception, exc_info):
        """
        Return an HttpResponse that displays a friendly error message.

        """
        callback, param_dict = resolver(request).resolve500()
        return callback(request, **param_dict)

    def debug_exception_processor(self, request, exception, exc_info):
        exc_type, exc_value, exc_tb = sys.exc_info()
        django_exception_handler = ExceptionReporter(request, exc_type, exc_value, exc_tb)
        return django_exception_handler.get_traceback_data()

    def log_exception(self, request, exception, exc_info):
        exc = self.debug_exception_processor(request, exception, exc_info)
        logger.exception(exc)

    def store_exception(self, request, exception, exc_info):
        exc = self.debug_exception_processor(request, exception, exc_info)

        date_and_hour_30_minute_back = datetime.datetime.now() - datetime.timedelta(minutes=30)
        date_and_hour_30_minute_back_formated = date_and_hour_30_minute_back.strftime('%Y-%m-%d %H:%M:%S')

        template = Template(TECHNICAL_500_TEMPLATE)
        template_text = Template(TECHNICAL_500_TEXT_TEMPLATE)

        server, created = SiteExceptionLogger.objects.get_or_create(
          exception_type=exc['exception_type'],
          exception_value=exc['exception_value']
        )

        exc.update({'obj': server.to_dict()})
        context = Context(exc)
        html = template.render(context)
        html_text = template_text.render(context)
        if not created:
            times = server.occurance
            server.occurance = times + 1
            server.rendered_html_debug = html
            server.rendered_html_debug_text = html_text
        elif created:
            server.uid = uuid.uuid4()
            server.exception_type = exc['exception_type']
            server.exception_value = exc['exception_value']
            server.rendered_html_debug = html
            server.rendered_html_debug_text = html_text
        try:
            json_ready = {}
            for frame in exc['frames']:
                frame['tb'] = {}
            exc['lastframe']['tb'] = {}
            json_ready.update({
                'django_info': {
                    'version': exc['django_version_info']
                },
                'request_obj': {
                    'method': exc['request'].META['REQUEST_METHOD'],
                    'get_raw_uri': exc['request'].get_raw_uri(),
                    'path_info': exc['request'].path_info,
                },
                'middleware': exc['settings']['MIDDLEWARE_CLASSES'],
                'installed_apps': exc['settings']['INSTALLED_APPS'],
                'sys_info': {
                    'sys_executable': exc['sys_executable'],
                    'sys_path': exc['sys_path'],
                    'sys_version_info': exc['sys_version_info'],
                },
                'server': {
                    'server_time': str(exc['server_time'])
                },
                'frames': exc['frames'],
                'lastframe': exc['lastframe'],
            })
            server.exception_traceback_json = json_ready
        except Exception as e:
            pass

        server.save()

        # create Tally counter for logs
        try:
            server_tally = server.siteexceptionloggertally_set.filter(
                created_at__gte=date_and_hour_30_minute_back_formated,
                exception=server
            ).order_by('-created_at')
            if server_tally:
                server_tally_obj = server_tally[0]
                total = server_tally_obj.total
                if total:
                    server_tally_obj.total = total + 1
                else:
                    server_tally_obj.total = 1
                server_tally_obj.save()
            else:
                server_tally_create = SiteExceptionLoggerTally.objects.create(
                    exception=server
                )
                server_tally_create.total = 1
                server_tally_create.save()
        except Exception as e:
            logger.error('Could Not create tally for server error')