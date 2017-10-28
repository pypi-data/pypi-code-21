from core_flavor.drf.test import APITestCase

from .views import ErrorView


class ExceptionsTests(APITestCase):

    def test_exception_handler(self):
        request = self.factory.get('/')
        response = ErrorView.as_view()(request)

        self.assertIsInstance(response.data['error'], dict)
