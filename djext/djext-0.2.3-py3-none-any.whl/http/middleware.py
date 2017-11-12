from django.http import HttpResponse, HttpResponseServerError
from django.utils.deprecation import MiddlewareMixin

from .exceptions import HttpError


class ExceptionResponseMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, HttpError):
            return HttpResponse(
                status=exception.status_code, reason=exception.reason)
        else:
            return HttpResponseServerError()
