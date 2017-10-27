import webtest

from ingredients_http.app import HTTPApplication
from ingredients_http.app_mount import ApplicationMount
from ingredients_http.test.base import APITestCase


class TWebApplication(HTTPApplication):
    pass


class TMountAppRoutes(ApplicationMount):
    def __init__(self, app: HTTPApplication):
        super().__init__(app=app, mount_point='/', routers_location='routes.app')


class TestApplication(APITestCase):
    def settings_module(self) -> str:
        return "ingredients_http.test.settings.application_settings"

    def app_cls(self):
        return TWebApplication

    def setup_mounts(self, app):
        app.register_mount(TMountAppRoutes(app))

    def test_params_validation(self, wsgi: webtest.TestApp):
        resp = wsgi.get("/foo/1")

        assert resp.json == {}

        resp = wsgi.get("/foo/notanint", status=400)

        assert resp.json == {
            'status': '400 Bad Request',
            'message': 'Query parameters are invalid or misconfigured.',
            'errors': [
                {
                    'detail': "Value 'notanint' is not int.",
                    'source': {
                        'parameter': 'foo_id'
                    }
                }
            ]
        }

    def test_payload_validation(self, wsgi: webtest.TestApp):
        resp = wsgi.post_json("/bar", params={"foo": "bar"})
        assert resp.json == {}

        resp = wsgi.post_json("/bar", params={}, status=422)
        assert resp.json == {
            'status': '422 Unprocessable Entity',
            'message': 'Data payload invalid or misconfigured.',
            'errors': [
                {
                    'detail': "This field is required.",
                    'source': {
                        'pointer': '/data/attributes/foo'
                    }
                }
            ]
        }

    def test_response_validation(self, wsgi: webtest.TestApp):
        resp = wsgi.get("/baz/bad", status=500)
        assert resp.json == {
            'status': '500 Internal Server Error',
            'message': 'Server response invalid or misconfigured.',
            'errors': [
                {
                    'detail': "This field is required.",
                    'source': {
                        'pointer': '/data/attributes/foo'
                    }
                }
            ]
        }

        resp = wsgi.get("/baz/good")
        assert resp.json == {
            "foo": "bar"
        }

    def test_response_list_validation(self, wsgi: webtest.TestApp):
        resp = wsgi.get("/qux/bad", status=500)
        assert resp.json == {
            'status': '500 Internal Server Error',
            'message': 'Server response invalid or misconfigured.',
            'errors': [
                {
                    'detail': "This field is required.",
                    'source': {
                        'pointer': '/data/attributes/foo'
                    }
                }
            ]
        }

        resp = wsgi.get("/qux/good")
        assert 'good_links' in resp.json
        assert len(resp.json['good_links']) == 0
        assert resp.json == {
            'good_links': [],
            'good': [
                {
                    'foo': 'bar',
                    'id': 1
                }
            ]
        }

        resp = wsgi.get("/qux/page")
        assert 'page_links' in resp.json
        assert len(resp.json['page_links']) == 1
        assert resp.json == {
            'page_links': [
                {
                    'href': 'http://localhost:80/qux/page?marker=1',
                    'rel': 'next'
                }
            ],
            'page': [
                {
                    'foo': 'bar',
                    'id': 1
                }
            ]
        }
