import collections

from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


def verbose_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        request = context['request']
        _request = request._request

        data = [
            (attr, getattr(_request, attr))
            for attr in ('version', 'sandbox')
            if hasattr(_request, attr)
        ]

        if hasattr(exc, 'auth_header'):
            data.append(('auth', exc.auth_header))

        kwargs = context['kwargs']

        if kwargs:
            data.append(('kwargs', kwargs))

        if isinstance(exc, ValidationError):
            detail = exc.get_full_details()
        else:
            detail = response.data.get('detail', getattr(exc, 'detail', ''))

        response.data = {
            'error': collections.OrderedDict([
                ('type', exc.__class__.__name__),
                ('detail', detail),
                ('context', collections.OrderedDict(data))
            ])
        }

    return response
