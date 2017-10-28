from unittest.mock import patch

from django.views.generic.base import View
from django.test import TestCase
from django.test.client import RequestFactory

from core_flavor import middleware


def _get_response(request):
    return View.as_view()(request)


class MiddlewareTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    @patch('core_flavor.middleware.logstash.logger')
    def test_middleware(self, logger):
        request = self.factory.get('/')
        logstash_middleware = middleware.RequestLoggerMiddleware(
            get_response=_get_response
        )

        logstash_middleware(request)
        self.assertEqual(logger.info.call_count, 1)
