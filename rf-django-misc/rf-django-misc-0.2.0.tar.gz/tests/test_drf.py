from django.test import RequestFactory
from django.test import TestCase

from rf_django_misc.drf.middleware import MethodOverrideMiddleware


class MethodOverrideMiddlewareTest(TestCase):

    def test_does_not_override_if_not_post(self):
        request = RequestFactory().get('/')
        MethodOverrideMiddleware().process_view(request, None, None, None)
        self.assertEqual(request.method, 'GET')

    def test_does_not_ovrrride_if_header_not_present(self):
        request = RequestFactory().post('/')
        MethodOverrideMiddleware().process_view(request, None, None, None)
        self.assertEqual(request.method, 'POST')

    def test_overrides_post_with_put(self):
        request = RequestFactory().post('/')
        request.META['HTTP_X_HTTP_METHOD_OVERRIDE'] = 'PUT'
        MethodOverrideMiddleware().process_view(request, None, None, None)
        self.assertEqual(request.method, 'PUT')
