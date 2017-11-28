import time
import json
from functools import wraps

from django_framework.django_helpers.exception_helpers import ExceptionHandler

from django.conf import settings
DEBUG_MODE = settings.DEBUG

try:
    SHOW_DEBUG_TRACEBACK = settings.SHOW_DEBUG_TRACEBACK
except:
    SHOW_DEBUG_TRACEBACK = False
    


def try_except_channels(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # normal run no errors
            return func(*args, **kwargs)
        except Exception, e:
            json_error = ExceptionHandler.error_to_json(e, show_traceback = SHOW_DEBUG_TRACEBACK)
            return {"meta_data" : {}, "error": json_error, 'status_code' : json_error['status_code']}

    return wrapper