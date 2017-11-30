from functools import wraps
from requests.exceptions import HTTPError
from rest_framework.response import Response
from django.conf import settings
from exception_handling import ExceptionHandler


DEBUG_MODE = settings.DEBUG

try:
    SHOW_DEBUG_TRACEBACK = settings.SHOW_DEBUG_TRACEBACK
except:
    SHOW_DEBUG_TRACEBACK = False

try:
    SHOW_DEBUG_ERROR = settings.SHOW_DEBUG_ERROR
except:
    SHOW_DEBUG_ERROR = False

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

            # not too sure why we need this?  have not tested far enough!
#             if isinstance(e, HTTPError):
#                 if DEBUG_MODE is True:
#                     return Response(e.response.content, status=e.response.status_code)
#                 else:
#                     try:
#                         return Response(e.response.json(), status=e.response.status_code)
#                     except Exception as e:
#                         return Response(e.response.content, status=e.response.status_code)

            if SHOW_DEBUG_ERROR == True:
                raise
            
            json_error = ExceptionHandler.error_to_json(e, show_traceback= SHOW_DEBUG_TRACEBACK)
            
            return Response({
                "meta_data" : {
                        "model": "error",
                        "type": "error",
                        "total_query_results": 1,
                        
                        }, 
                        "error": json_error}, status=json_error['status_code'])

    return wrapper
