from django.urls import reverse
from functools import partialmethod
from oauth2_provider.models import Application
from rest_framework.test import APIClient


class APIUnitTestMixin(object):
    HTTP_DELETE = 'DELETE'
    HTTP_GET = 'GET'
    HTTP_OPTIONS = 'OPTIONS'
    HTTP_PATCH = 'PATCH'
    HTTP_POST = 'POST'
    HTTP_PUT = 'PUT'

    def setUp(self):
        self.client = APIClient()
        self.application = Application.objects.create(
            name='Unit Testing', client_type='public', authorization_grant_type='password'
        )

    def _get_request_func(self, http_method):
        method = getattr(self.client, http_method.lower())
        if not method:
            raise Exception('Request type %s not valid' % type)

        return method

    def send(self, http_method, url, **kwargs):
        url_kwargs = kwargs.pop('url_kwargs', {})
        request_format = kwargs.pop('format', 'json')

        func = self._get_request_func(http_method)
        return func(
            reverse(url, kwargs=url_kwargs),
            format=request_format,
            **kwargs
        )

    delete = partialmethod(send, HTTP_DELETE)
    get = partialmethod(send, HTTP_GET)
    options = partialmethod(send, HTTP_OPTIONS)
    patch = partialmethod(send, HTTP_PATCH)
    post = partialmethod(send, HTTP_POST)
    put = partialmethod(send, HTTP_PUT)

    def login(self, user):
        password = '(oolFox88%'
        user.set_password(password)
        user.save()
        return self.post('token', **{
            'grant_type': self.application.authorization_grant_type,
            'username': user.username,
            'password': password,
            'client_id': self.application.client_id,
            'client_secret': self.application.client_secret
        })

    def authenticate(self, user=None):
        self.client.credentials()
        if user:
            response = self.login(user)
            self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access_token'])

    @staticmethod
    def modify_data(data={}, exclude=[], injections={}):
        data = {**data, **injections}
        for field in exclude:
            data.pop(field, None)

        return data
