import json
import logging

from collections import OrderedDict
from django.utils.translation import get_language, to_locale

from .. import settings as core_settings
from ..utils import get_client_ip


__all__ = ['RequestLoggerMiddleware']


logger = logging.getLogger(
    core_settings.CORE_REQUEST_LOGGER_NAME
)


class RequestLoggerMiddleware(object):
    META_KEYS = (
        'CSRF_COOKIE',
        'DJANGO_SETTINGS',
        'HOSTNAME',
        'LANG',
        'PYTHON_PIP_VERSION',
        'PYTHON_VERSION',
        'REMOTE_ADDR',
        'REMOTE_HOST',
        'SERVER_NAME',
        'SERVER_PORT',
        'SERVER_PROTOCOL',
        'SERVER_SOFTWARE',
        'TZ'
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        data = OrderedDict({
            'content_type': request.content_type,
            'method': request.method,
            'path': request.path,
            'path_info': request.path_info,
            'uri': request.build_absolute_uri(),
            'is_ajax': request.is_ajax(),
            'is_secure': request.is_secure(),
            'sandbox': getattr(request, 'sandbox', None),
            'version': getattr(request, 'version', None),
            'format': getattr(request, 'format', None),
            'language': get_language(),
            'locale': to_locale(get_language()),
            'GET': json.dumps(request.GET, indent=2),
            'meta': {},
            'headers': {},
            'response': self.get_response_fields(response),
            'src_ip': get_client_ip(request),
            'user': self.get_user_fields(request)
        })

        if hasattr(request, 'host'):
            data['host'] = request.host.name

        for attr, value in request.META.items():
            if attr.startswith('HTTP_'):
                data['headers'][self.parse_header(attr[5:])] = value

            elif attr in self.META_KEYS:
                data['meta'][self.parse_header(attr)] = value

        logger.info(request.path_info, extra=data)
        return response

    @classmethod
    def parse_header(cls, header):
        return header.lower().replace('-', '_')

    @classmethod
    def get_response_fields(cls, response):
        data = OrderedDict({
            'status_code': response.status_code,
            'headers': {
                cls.parse_header(k): str(v) for k, v in response.items()
            }
        })

        if (400 <= response.status_code < 500) and\
                isinstance(getattr(response, 'data', None), dict):
            data['content'] = response.data
        return data

    @classmethod
    def get_user_fields(cls, request):
        user = getattr(request, 'user', None)

        if user is not None and user.is_authenticated():
            return OrderedDict({
                'email': user.email,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'language': user.language,
                'last_login': user.last_login.isoformat(),
                'first_name': user.first_name,
                'last_name': user.last_name
            })
        return None
