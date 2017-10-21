from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.response import Response
import httpretty
import pytest
import webtest


httpretty.HTTPretty.allow_net_connect = False


class FakeError(Exception):
    pass


def include_testing_views(config):
    def view_ok(request):
        return Response(b'hello')
    config.add_route(name='route_ok', pattern='/ok')
    config.add_view(view_ok, route_name='route_ok')

    def view_raise_error(request):
        raise HTTPInternalServerError()
    config.add_route(name='raise_error', pattern='/raise_error')
    config.add_view(view_raise_error, route_name='raise_error')

    def view_raise_custom_error(request):
        raise FakeError()
    config.add_route(name='raise_custom_error', pattern='/raise_custom_error')
    config.add_view(view_raise_custom_error, route_name='raise_custom_error')


@pytest.fixture
def bugsnag_ok():
    httpretty.enable()
    httpretty.register_uri('POST', 'https://notify.bugsnag.com', status=200)
    yield
    httpretty.disable()


@pytest.fixture
def bugsnag_failure():
    httpretty.enable()
    httpretty.register_uri('POST', 'https://notify.bugsnag.com', status=500)
    yield
    httpretty.disable()


@pytest.fixture(scope='session')
def test_app():
    # Settings needed to get bugsnag to actually send a notification
    settings = {
        'bugsnag.api_key': 'FAKE_KEY',
        'bugsnag.asynchronous': 'false',
    }
    config = Configurator(settings=settings)
    config.include('pyramid_bugsnag')
    config.include(include_testing_views)

    app = config.make_wsgi_app()
    return webtest.TestApp(app)


def test_ok(test_app, bugsnag_ok):
    test_app.get('/ok')

    assert not httpretty.has_request()


def test_not_found(test_app, bugsnag_ok, capsys):
    test_app.get('/unknown_route', status=404)

    assert httpretty.has_request()

    out, err = capsys.readouterr()
    assert not err


def test_raise_error(test_app, bugsnag_ok):
    test_app.get('/raise_error', status=500)

    assert httpretty.has_request()


def test_raise_custom_error(test_app, bugsnag_ok):
    with pytest.raises(FakeError):
        test_app.get('/raise_custom_error', status=500)

    assert httpretty.has_request()


def test_bugsnag_failure(test_app, bugsnag_failure):
    test_app.get('/raise_error', status=500)

    assert httpretty.has_request()
