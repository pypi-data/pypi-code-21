from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class Request(object):
    TYPE_DELETE = 'DELETE'
    TYPE_GET = 'GET'
    TYPE_OPTIONS = 'OPTIONS'
    TYPE_PATCH = 'PATCH'
    TYPE_POST = 'POST'
    TYPE_PUT = 'PUT'
        

class BaseRestUnitTest(TestCase):
    fixtures = []
    url = ''
    users = {}

    def setUp(self):
        self.client = APIClient()

    def authenticate(self, user=None):
        self.client.credentials()
        if user:
            token, created = Token.objects.get_or_create(user=user)
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    @staticmethod
    def modify_data(data={}, exclude=[], injections={}):
        data = {**data, **injections}
        for field in exclude:
            data.pop(field, None)

        return data
    
    def _send_request(self, type, url_kwargs=None, format='json', **kwargs):
        method = getattr(self.client, type.lower())
        if not method:
            raise Exception('Request type %s not valid' % type)

        return method(
            reverse(self.url, kwargs=url_kwargs),
            format=format,
            **kwargs
        )
    
    def delete(self, url_kwargs=None, format='json', **kwargs):
        return self._send_request(Request.TYPE_DELETE, url_kwargs=url_kwargs, format=format, **kwargs)
    
    def get(self, url_kwargs=None, format='json', **kwargs):
        return self._send_request(Request.TYPE_GET, url_kwargs=url_kwargs, format=format, **kwargs)
    
    def options(self, url_kwargs=None, format='json', **kwargs):
        return self._send_request(Request.TYPE_OPTIONS, url_kwargs=url_kwargs, format=format, **kwargs)
    
    def patch(self, url_kwargs=None, format='json', **kwargs):
        return self._send_request(Request.TYPE_PATCH, url_kwargs=url_kwargs, format=format, **kwargs)

    def post(self, url_kwargs=None, format='json', **kwargs):
        return self._send_request(Request.TYPE_POST, url_kwargs=url_kwargs, format=format, **kwargs)
    
    def put(self, url_kwargs=None, format='json', **kwargs):
        return self._send_request(Request.TYPE_PUT, url=url_kwargs, format=format, **kwargs)

    def list(self, url_kwargs=None, format='json', **kwargs):
        return self.get(url_kwargs=url_kwargs, format=format, **kwargs)

    def create(self, url_kwargs=None, format='json', **kwargs):
        return self.post(url_kwargs=url_kwargs, format=format, **kwargs)

    def retrieve(self, url_kwargs=None, format='json', **kwargs):
        return self.get(url_kwargs=url_kwargs, format=format, **kwargs)

    def update(self, url_kwargs=None, format='json', **kwargs):
        return self.patch(url_kwargs=url_kwargs, format=format, **kwargs)

    def destroy(self, url_kwargs=None, format='json', **kwargs):
        return self.destroy(url_kwargs=url_kwargs, format=format, **kwargs)
