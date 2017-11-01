import logging
import threading
import urllib.parse
import uuid

import flask
import requests
from flask_httpauth import HTTPBasicAuth

from sepiida.errors import APIException, AuthenticationException, Error
import sepiida.environment

try:
    import uwsgi
except ImportError:
    uwsgi = None

auth = HTTPBasicAuth()
LOGGER = logging.getLogger(__name__)

def register_session_handlers(app, whitelist=None):
    app.before_request(require_user)
    whitelist = whitelist or []
    for endpoint in whitelist:
        public_endpoint(app, endpoint)

    app.config['PUBLIC_ENDPOINTS'] = app.config.get('PUBLIC_ENDPOINTS', []) + whitelist
    settings = sepiida.environment.get()
    @auth.verify_password
    def verify_password(username, password): # pylint: disable=unused-variable
        if username == 'api' and password == settings.API_TOKEN:
            return True
        else:
            url = urllib.parse.urljoin(settings.USER_SERVICE, '/sessions/')
            response = requests.get(url, auth=(username, password))
            if not response.status_code == 200:
                return False
            flask.g.current_user = response.json()
            return True

def add_origin_handler(app):
    def extract_origin():
        if uwsgi:
            uwsgi.set_logvar('origin', flask.request.headers.get('Origin', 'none'))
    app.before_request(extract_origin)

def add_request_id_handler(app):
    def extract_request_id():
        flask.g.request_id = flask.request.headers.get('Request-ID', str(uuid.uuid4()))
        if uwsgi:
            uwsgi.set_logvar('request_id', flask.g.request_id)
            uwsgi.set_logvar('thread_id', str(threading.get_ident()))
    def add_request_id(response):
        response.headers['Request-ID'] = current_request_id()
        return response
    app.before_request(extract_request_id)
    app.after_request(add_request_id)

def current_request_id():
    if flask.has_request_context():
        return flask.g.get('request_id', 'none')
    return 'backend'

def current_user_uri():
    try:
        return flask.g.current_user.get('uri', None)
    except AttributeError:
        return None

def current_user():
    if flask.g.endpoint_authenticated:
        return flask.g.current_user

    if 'uri' not in flask.g.current_user:
        return

    if 'uuid' in flask.g.current_user:
        return flask.g.current_user

    settings = sepiida.environment.get()
    url = urllib.parse.urljoin(settings.USER_SERVICE, '/sessions/')
    cookies = { 'session': flask.request.cookies.get('session', None) }
    response = requests.get(url, cookies=cookies)
    if not response.status_code == 200:
        raise AuthenticationException(
                status_code=400,
                error_code='retrieving-user-details-error',
                title="An error occured while retrieving the user details.")
    flask.g.current_user = response.json()
    return flask.g.current_user


def is_whitelisted(endpoint, method):
    blueprint, _, basename = endpoint.rpartition('.')
    basename = basename or blueprint

    endpoint_with_method = '{}.{}'.format(endpoint, method.lower())
    defaults = flask.request.url_rule.defaults
    if defaults and not defaults.get('_single_resource', False) and method == "GET":
        endpoint_with_method = '{}.list'.format(endpoint)

    public_endpoints = flask.current_app.config['PUBLIC_ENDPOINTS']
    return any([
        basename             in public_endpoints,
        endpoint             in public_endpoints,
        endpoint_with_method in public_endpoints,
    ])


def public_endpoint(app, f):
    try:
        endpoint_name = f.__name__
    except AttributeError:
        endpoint_name = f
    app.config['PUBLIC_ENDPOINTS'] = app.config.get('PUBLIC_ENDPOINTS', []) + [endpoint_name]

def get_endpoint_authentication():
    resource = getattr(flask.current_app, 'endpoints', {}).get(flask.request.endpoint, None)
    if resource:
        try:
            return resource.authenticate()
        except Error as e:
            raise APIException(errors=[e])

def require_user():
    # pylint: disable=too-many-branches
    flask.g.current_user = {}
    flask.g.endpoint_authenticated = False
    if 'Access-Control-Request-Method' in flask.request.headers and flask.request.method == 'OPTIONS':
        return

    elif not flask.request.endpoint:
        return

    elif flask.request.path.startswith(flask.current_app.static_url_path):
        return

    elif is_whitelisted(flask.request.endpoint, flask.request.method):
        return

    endpoint_authentication = get_endpoint_authentication()
    if endpoint_authentication:
        flask.g.current_user = endpoint_authentication
        flask.g.endpoint_authenticated = True
    elif flask.request.authorization:
        if auth.authenticate(flask.request.authorization, flask.request.authorization.password):
            return
        else:
            raise AuthenticationException(
                    status_code=403,
                    error_code='invalid-credentials',
                    title='The API key and secret you provided were not recognized')

    elif 'session' not in flask.request.cookies and 'Authorization' not in flask.request.headers:
        raise AuthenticationException(
                status_code=403,
                error_code='no-credentials-provided',
                title="You must include a valid session cookie or an API token and secret "
                    "encoded in your Authorization header according to Basic Auth standards (RFC 2617)")

    elif 'Authorization' in flask.request.headers:
        raise AuthenticationException(
                status_code=400,
                error_code='not-well-formed-authorization-header',
                title="The authorization header you have provided was not properly formatted. "
                    "Please see RFC 2617")

    elif not flask.session:
        raise AuthenticationException(
                status_code=403,
                error_code='empty-session-provided',
                title="The session cookie you have provided does not contain any data")

    elif 'user_uri' not in flask.session:
        raise AuthenticationException(
                status_code=403,
                error_code='invalid-session-provided',
                title="The session cookie you have provided does not contain valid data")

    elif 'user_uri' in flask.session:
        flask.g.current_user['uri'] = flask.session['user_uri']

        if not flask.g.current_user['uri']:
            raise AuthenticationException(
                    status_code=400,
                    error_code='unkown-user-error',
                    title="The user information you have provided is not valid or does not exist.")

    else:
        raise AuthenticationException(
                status_code=403,
                error_code='unkown-authentication-error',
                title="Not sure what happened, but authentication failed. Tell Authentise")

def is_api_user():
    if flask.request.authorization:
        password = auth.get_password_callback(flask.request.authorization.username)
        return auth.authenticate(flask.request.authorization, password)
    return False

def is_internal_user():
    settings = sepiida.environment.get()
    return bool(flask.request.authorization) and \
           flask.request.authorization.username == 'api' and \
           flask.request.authorization.password == settings.API_TOKEN
