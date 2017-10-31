from functools import wraps
from requests.exceptions import HTTPError
from rest_framework.response import Response
from django.conf import settings
from exception_handling import ExceptionHandler


DEBUG_MODE = settings.DEBUG

def try_except(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            json_error = ExceptionHandler.error_to_json(e)
            return json_error

    return wrapper


def try_except_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # normal run no errors
            return func(*args, **kwargs)
        except Exception, e:
            # an error has occured!
            if settings.DEBUG is False:  # if we are in debug mode, we want the fancy django HTML
                raise
            
            # not too sure why we need this?  have not tested far enough!
#             if isinstance(e, HTTPError):
#                 if DEBUG_MODE is True:
#                     return Response(e.response.content, status=e.response.status_code)
#                 else:
#                     try:
#                         return Response(e.response.json(), status=e.response.status_code)
#                     except Exception as e:
#                         return Response(e.response.content, status=e.response.status_code)


            json_error = ExceptionHandler.error_to_json(e)
            
            return Response({
                "meta_data" : {
                        "model": "error",
                        "type": "error",
                        "total_query_results": 1,
                        
                        }, 
                        "error": json_error}, status=json_error['status_code'])

    return wrapper
