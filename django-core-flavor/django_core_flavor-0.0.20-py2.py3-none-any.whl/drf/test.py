from django.conf import settings

from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase as BaseAPITestCase

from . import factories


class APITestCase(BaseAPITestCase):
    VERSION = 'v1'

    def setUp(self):
        self.factory = APIRequestFactory()
        self.access_token = factories.AccessTokenFactory()
        self.user = self.access_token.user

        self.client = self.get_client(
            HTTP_AUTHORIZATION="Bearer {}"
            .format(self.access_token.token)
        )

        self.auth_client = self.get_client()
        self.auth_client.force_authenticate(user=self.user)
        self.anonymous_client = self.get_client()

    def get_client(self, sandbox=False, **credentials):
        vnd_site_name = settings.SITE_NAME

        if sandbox:
            vnd_site_name += '.sandbox'

        credentials.update({
            'HTTP_HOST': "api.{}".format(settings.SITE_NAME),
            'HTTP_ACCEPT': "application/vnd.{0}.{1}+json"
            .format(vnd_site_name, self.VERSION)
        })

        client = self.client_class()
        client.credentials(**credentials)
        return client
