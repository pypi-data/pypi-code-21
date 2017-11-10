from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework import exceptions, status
from rest_framework.compat import set_rollback
from rest_framework.response import Response
from SweetPy import response_plus

def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        # if isinstance(exc.detail, (list, dict)):
        #     data = exc.detail
        # else:
        #     data = {'detail': exc.detail}
        data = {}
        code, message = response_plus.get_message_by_httpstatus_code(response_plus.APIResponseHTTPCode.FAIL)
        data['code'] = code
        data['message'] = message

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    elif isinstance(exc, Http404):
        # msg = _('Not found.')
        # data = {'detail': six.text_type(msg)}
        data = {}
        code, message = response_plus.get_message_by_httpstatus_code(response_plus.APIResponseHTTPCode.NOT_FOUND)
        data['code'] = code
        data['message'] = message
        set_rollback()
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    elif isinstance(exc, PermissionDenied):
        # msg = _('Permission denied.')
        # data = {'detail': six.text_type(msg)}
        data = {}
        code, message = response_plus.get_message_by_httpstatus_code(response_plus.APIResponseHTTPCode.UNAUTHORIZED)
        data['code'] = code
        data['message'] = message
        set_rollback()
        return Response(data, status=status.HTTP_403_FORBIDDEN)

    return None