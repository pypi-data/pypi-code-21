from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import ugettext_lazy as _

import logging

logger = logging.getLogger("django.restresp")


class RespStatus:
    """ Status object for custom response """

    def __init__(self):
        pass

    class OK:
        msg = _('ok')
        http_code = status.HTTP_200_OK
        type = 'OK'

    class DELETED:
        msg = _('Marked for deletion')
        http_code = status.HTTP_202_ACCEPTED
        type = 'OK'

    class CREATED:
        msg = _('Created')
        http_code = status.HTTP_201_CREATED
        type = 'OK'

    class PARTIALLY_ACCEPTABLE:
        msg = _('Response can be not reliable')
        http_code = status.HTTP_206_PARTIAL_CONTENT
        type = 'OK'

    class UNAUTHORIZED:
        msg = _('Unauthorized resource')
        http_code = status.HTTP_401_UNAUTHORIZED
        type = 'UNAUTHORIZED'

    class NOT_FOUND:
        msg = _('Resource not found')
        http_code = status.HTTP_404_NOT_FOUND
        type = 'NOTFOUND'

    class ERROR_DATA:
        msg = _('Wrong data provided')
        http_code = status.HTTP_400_BAD_REQUEST
        type = 'ERROR'

    class MISSING_DATA:
        msg = _('missing data')
        http_code = status.HTTP_400_BAD_REQUEST
        type = 'MISSING_DATA'

    class GENERIC_ERROR:
        msg = _('generic error')
        http_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        type = 'GENERIC_ERROR'


class Responder(object):
    def __init__(self, payload=list(), status=RespStatus.OK, msg=None, errors=[], pagination=dict()):
        self.payload = payload if isinstance(payload, list) else [payload]
        self.status = status
        self.msg = msg
        self.errors = errors if isinstance(errors, list) else [errors]
        self.pagination = pagination

    def as_response(self, format='json'):
        #TODO: implement format switch
        resp_status = self.status

        response_body = dict(msg=self.msg or resp_status.msg,
                             payload=self.payload,
                             errors=self.errors,
                             pagination=self.pagination,
                             )

        response = Response(response_body, status=resp_status.http_code)

        return response

    @staticmethod
    def not_found(msg=None):
        r = Responder(status=RespStatus.NOT_FOUND)
        r.errors.append(msg)

        return r.as_response()


def _verify_mandatory(data, fields, kind='dict', all=True):
    errors = []
    founds = 0

    if kind == 'dict':
        for f in fields:
            if not all and founds > 0:
                break
            if not data.get(f):
                errors.append(dict(field=f, msg='Missing %s' % f))
            else:
                founds += 1

    if not all and founds > 0:
        return []

    return errors

def validate_data(fields, check_all=True):
    """
    :param fields: fiels that must be present in request data
    :param check_all: default True set a strict validation: all elements must be present
    :return: error or let pass the check
    """
    def wrap(f):
        def wrapped_f(*args, **kwargs):
            request = args[0]
            if request.method == 'POST':
                data = request.POST
            if request.method == 'GET':
                data = request.GET
            checks = _verify_mandatory(data, fields, all=check_all)
            if checks:
                return Responder(status=RespStatus.MISSING_DATA, errors=checks).as_response()

            return f(*args, **kwargs)

        return wrapped_f
    return wrap
