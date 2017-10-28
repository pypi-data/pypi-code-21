import re

from django.conf import settings
from core_flavor.drf import middleware
from core_flavor.drf.test import APITestCase


class VersioningTests(APITestCase):
    X_MEDIA_TYPE_PATTERN = re.compile(
        r"^{}(?P<sandbox>.sandbox)?.(?P<version>v\d+);"
        r" format=(?P<format>\S+)"
        .format(settings.SITE_NAME))

    def get_media_type(self, response):
        return self.X_MEDIA_TYPE_PATTERN\
            .match(
                response.get(
                    middleware.VersioningMiddleware.X_MEDIA_TYPE
                )
            )\
            .groupdict()

    def test_versioning_url(self):
        version_url = 'v2'
        response = self.client.get("/{}/test".format(version_url))

        self.assertEqual(
            self.get_media_type(response)['version'],
            version_url)

    def test_versioning_media_type(self):
        response = self.client.get('/')

        self.assertEqual(
            self.get_media_type(response)['version'],
            self.VERSION)

    def test_versioning_format(self):
        self.client._credentials['HTTP_ACCEPT'] =\
            self.client._credentials['HTTP_ACCEPT']\
            .replace('json', 'api')

        response = self.client.get('/')
        self.assertEqual(self.get_media_type(response)['format'], 'api')

    def test_versioning_sandbox(self):
        response = self.get_client(sandbox=True).get('/')
        self.assertIsNotNone(self.get_media_type(response)['sandbox'])
