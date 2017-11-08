"""
@summary: This middleware is used to let browser be able to access api cross origin
Add following settings in Django settings.py
XS_SHARING_ALLOWED_ORIGINS = '*'
XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']
XS_SHARING_ALLOWED_HEADERS = ['Content-Type', '*']
XS_SHARING_ALLOWED_CREDENTIALS = True
"""

from django import http
from django.conf import settings


def share_resource_middleware(get_response):
    def middleware(request):
        response = get_response(request)
        try:
            XS_SHARING_ALLOWED_ORIGINS = settings.XS_SHARING_ALLOWED_ORIGINS
            XS_SHARING_ALLOWED_METHODS = settings.XS_SHARING_ALLOWED_METHODS
            XS_SHARING_ALLOWED_HEADERS = settings.XS_SHARING_ALLOWED_HEADERS
            XS_SHARING_ALLOWED_CREDENTIALS = settings.XS_SHARING_ALLOWED_CREDENTIALS
            XS_ACCESS_CONTROL_EXPOSE_HEADERS = settings.XS_ACCESS_CONTROL_EXPOSE_HEADERS
        except AttributeError:
            XS_SHARING_ALLOWED_ORIGINS = '*'
            XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']
            XS_SHARING_ALLOWED_HEADERS = ['Content-Type', '*']
            XS_SHARING_ALLOWED_CREDENTIALS = 'true'
            XS_ACCESS_CONTROL_EXPOSE_HEADERS = ['Content-Type', '*']

        response['Access-Control-Allow-Origin'] = XS_SHARING_ALLOWED_ORIGINS
        response['Access-Control-Allow-Methods'] = ",".join(XS_SHARING_ALLOWED_METHODS)
        response['Access-Control-Allow-Headers'] = ",".join(XS_SHARING_ALLOWED_HEADERS)
        response['Access-Control-Allow-Credentials'] = XS_SHARING_ALLOWED_CREDENTIALS
        response['Access-Control-Expose-Headers'] = ",".join(XS_ACCESS_CONTROL_EXPOSE_HEADERS)

        return response

    return middleware