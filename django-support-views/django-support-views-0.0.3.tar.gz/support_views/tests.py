from django.test import RequestFactory, SimpleTestCase
from django.views.generic import TemplateView

from .views import SupportLogView


class BrowserVerificationTest(SimpleTestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def testSupportLog(self):
        response = SupportLogView.as_view()(self.factory.post(
            '/support/log/',
            dict(
                message="Help!",
                image="data:image/gif;base64,R0lGODlhAQABAPAAAP8REf///yH5BAAAAAAALAAAAAABAAEAAAICRAEAOw=="
            )
        ))
        self.assertEqual(response.content, "OK")
