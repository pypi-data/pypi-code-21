from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.utils.deprecation import MiddlewareMixin

from .exceptions import HttpError


class ExceptionResponseMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, HttpError):
            return HttpResponse(
                status=exception.status_code, reason=exception.reason)
        elif not isinstance(exception, Http404):
            if not settings.DEBUG:
                return HttpResponseServerError()
