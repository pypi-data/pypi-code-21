from rest_framework import status
from requests.exceptions import HTTPError
from django.core.exceptions import ObjectDoesNotExist, FieldError
from django_framework.helpers.traceback_helpers import traceback_to_str

from rest_framework.serializers import ValidationError

ERRORS = {}  # an end catch all
ERRORS[TypeError] = status.HTTP_412_PRECONDITION_FAILED
ERRORS[IOError] = status.HTTP_412_PRECONDITION_FAILED
ERRORS[ValueError] = status.HTTP_412_PRECONDITION_FAILED
ERRORS[ObjectDoesNotExist] = status.HTTP_400_BAD_REQUEST
ERRORS[FieldError] = status.HTTP_400_BAD_REQUEST
ERRORS[NotImplemented] = status.HTTP_501_NOT_IMPLEMENTED


ERRORS[ValidationError] = status.HTTP_412_PRECONDITION_FAILED

class ExceptionHandler(object):

    @classmethod
    def error_to_json(cls, err, show_traceback = False):
        if isinstance(err, HTTPError):
            try:
                return err.response.json()
            except Exception:
                return err.response.content
        
        if show_traceback == True:
            traceback = traceback_to_str(exception=err),  # backend traceback
        else:
            traceback = 'Please use debug mode to show traceback!'
        return {
            'message': str(err),   # the string error received
            'traceback': traceback,
            'error_code': cls.get_error_code(err=err), 
            'status_code': cls.get_status_code(err=err), # usually the HTTP STATUS CODE
            'notes' : cls.get_notes(err = err),
        }

    @classmethod
    def get_status_code(cls, err):
        try:
            return err.http_status
        except AttributeError:
            if isinstance(err, HTTPError):
                return HTTPError.response.status
            return ERRORS.get(err.__class__, 500)

    @classmethod
    def get_error_code(cls, err):
        try:
            return err.error_code
        except AttributeError:
            if isinstance(err, HTTPError):
                return HTTPError.response.get_json().get("error", {}).get("error_code", 5000)
            return 5000

    @classmethod
    def get_notes(cls, err):
        try:
            return err.notes
        except AttributeError:
            return None