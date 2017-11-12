from django.utils.deprecation import MiddlewareMixin

from djext.http.exceptions import HttpError
from djext.json.http.response import JsonResponse, JsonResponseServerError


class JsonExceptionResponseMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        accept = request.META.get('HTTP_ACCEPT')
        if accept and accept == 'application/json':
            if isinstance(exception, HttpError):
                return JsonResponse(
                    status=exception.status_code, reason=exception.reason)
            else:
                return JsonResponseServerError()
