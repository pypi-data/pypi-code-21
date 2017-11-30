import urllib.parse

import flask
import werkzeug.exceptions
import werkzeug.routing

import sepiida.errors


class FakeRequest():
    def __init__(self, method, url, app):
        self.environ = {
            'CONTENT_LENGTH'    : '0',
            'CONTENT_TYPE'      : '',
            'HTTP_HOST'         : app.config.get('SERVER_NAME') or 'localhost',
            'PATH_INFO'         : url,
            'QUERY_STRING'      : '',
            'REQUEST_METHOD'    : method,
            'SERVER_NAME'       : app.config.get('SERVER_NAME') or 'localhost',
            'wsgi.url_scheme'   : 'http',
        }

def extract_parameters(app, method, url):
    if url.startswith('http'):
        parsed = urllib.parse.urlparse(url)
        url = parsed.path
    request = FakeRequest(method, url, flask.current_app)
    adapter = app.create_url_adapter(request)
    try:
        return adapter.match()
    except (werkzeug.exceptions.NotFound, werkzeug.exceptions.MethodNotAllowed):
        return None, {}
    except werkzeug.routing.RequestRedirect as e:
        return extract_parameters(app, method, e.new_url)

def uri(endpoint, uuid=None, method='GET', **kwargs):
    try:
        return flask.url_for(endpoint, uuid=uuid, _external=True, _method=method, _scheme='https', _single_resource=True, **kwargs)
    except werkzeug.routing.BuildError:
        error = (
            "Failed to build a URI. You may have attempted to create a URI on a resource ({}) "
            "that does not have a get() method or supplied a UUID when it expects an integer ID or vice-versa."
        ).format(endpoint)
        raise sepiida.errors.RoutingError(error)
