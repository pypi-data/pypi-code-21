import base64
import collections
import contextlib
import copy
import json as JSON
import logging
import os
import re
import urllib.parse
import zlib
from uuid import uuid4

import attrdict
import httpretty as HTTPretty
import itsdangerous
import pytest
import werkzeug.urls

import sepiida.backend
import sepiida.environment
import sepiida.jwt
import sepiida.parsing
import sepiida.permissions
import sepiida.requests

LOGGER = logging.getLogger(__name__)

class JSONClient():
    def __init__(self, client):
        self.client = client

    def _do_send(self, *args, method, json, **kwargs):
        if 'data' in kwargs:
            raise Exception("Don't specify a data parameter when using the JSONClient")
        data = JSON.dumps(json)
        headers = kwargs.pop('headers', {})
        headers = headers or {}
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'

        auth = kwargs.pop('auth', ())
        if auth:
            headers['Authorization'] = _basic_auth(*auth)

        jwt = kwargs.pop('jwt', None)
        if jwt:
            headers['jwt'] = sepiida.jwt.encode(payload=json, **jwt)

        method = getattr(self.client, method)
        return method(*args, data=data, headers=headers, **kwargs)

    def post(self, *args, json, **kwargs):
        return self._do_send(*args, json=json, method='post', **kwargs)

    def put(self, *args, json, **kwargs):
        return self._do_send(*args, json=json, method='put', **kwargs)

    def get(self, *args, **kwargs):
        headers = kwargs.pop('headers', {})
        headers = headers or {}
        auth = kwargs.pop('auth', ())
        if auth:
            headers['Authorization'] = _basic_auth(*auth)
        headers['Accept'] = 'application/json'

        jwt = kwargs.pop('jwt', None)
        if jwt:
            headers['jwt'] = sepiida.jwt.encode(payload='', **jwt)
        return self.client.get(*args, headers=headers, **kwargs)

    def options(self, *args, **kwargs):
        headers = kwargs.pop('headers', {})
        headers = headers or {}
        headers['Content-Type'] = 'application/json'
        return self.client.options(*args, headers=headers, **kwargs)

    def __getattr__(self, name):
        return getattr(self.client, name)

@pytest.yield_fixture
def json_client(app):
    with app.test_client() as client:
        yield JSONClient(client)

@pytest.fixture
def make_session(app):
    @contextlib.contextmanager
    def _inner(user_uri):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_uri'] = user_uri
            yield JSONClient(client)
    return _inner

@pytest.yield_fixture
def json_client_session(make_session, user): # pylint: disable=redefined-outer-name
    with make_session(user['uri']) as session:
        yield session

@pytest.yield_fixture
def httpretty():
    import socket
    old_socket_type = socket.SocketType
    HTTPretty.enable()
    yield HTTPretty
    HTTPretty.disable()
    socket.SocketType = old_socket_type
    HTTPretty.reset()

def _basic_auth(username, password):
    credentials = '{}:{}'.format(username, password).encode('utf-8')
    return 'Basic {}'.format(base64.b64encode(credentials).decode('utf-8'))

@pytest.fixture()
def basic_auth():
    return _basic_auth

@pytest.fixture
def user():
    uuid = str(uuid4())
    return {
        'name'          : 'Kenny Powers',
        'password'      : 'kpow-was-here',
        'uri'           : 'https://users.service/users/{}'.format(uuid),
        'username'      : 'kpowers',
        'uuid'          : uuid,
        'emails'        : [{
            'uuid'      : str(uuid4()),
            'user_uuid' : uuid,
            'email'     : 'kenny@powers.com',
        }],
    }

@pytest.fixture
def pao_user(httpretty, settings, user): # pylint: disable=redefined-outer-name
    httpretty.register_uri(
        httpretty.GET,
        settings.USER_SERVICE + '/sessions/',
        body=JSON.dumps(user),
        status=200
    )

    httpretty.register_uri(
        httpretty.GET,
        user['uri'],
        body=JSON.dumps(user),
        status=200
    )

    return user

def get_cookie_value(request, name):
    headers = [value for name, value in request.headers.items() if name == 'Cookie']
    headers = [value for value in headers if value.startswith(name + '=')]
    name, _, value = headers[-1].partition('=') if headers else (None, None, None)
    return value

def get_session_data(app, request):
    serializer = app.session_interface.get_signing_serializer(app)
    session_data = get_cookie_value(request, 'session')
    session = serializer.loads(session_data) if session_data else {}
    return session

def _get_session(headers):
    for key, value in headers.items():
        if key == 'Cookie' and value.startswith('session='):
            encoded = value[len('session='):]
            compressed = encoded.startswith('.')
            encoded = encoded[1:] if compressed else encoded
            content = encoded.split('.')[0]
            data = itsdangerous.base64_decode(content)
            raw = zlib.decompress(data) if compressed else data
            session = JSON.loads(raw.decode('utf-8'))
            return session
    return {}

def _extract_filters(request):
    body = request.body
    if not (body or request.querystring):
        return {}
    if request.body:
        search = werkzeug.urls.url_decode(body, charset='utf-8', errors='strict')
        filters = [sepiida.parsing.FilterArgument(k, [v]) for k, v in search.items() if k.startswith('filter')]
    else:
        search = request.querystring
        filters = [sepiida.parsing.FilterArgument(k, v) for k, v in search.items() if k.startswith('filter')]
    return filters

def _filter_by_holder(grants, session):
    # Apply implicit permissions filter. This is to mimic the fact that a
    # user can only list permissions that grants them something, either by
    # belonging to a group or by being themselves
    # This is not perfectly accurate - we don't mimic group behavior
    # here. Sorry.
    user_uri = session.get('user_uri')
    if user_uri:
        LOGGER.debug("Filtering out grants whose holder or creator are not %s", user_uri)
        grants = [g for g in grants if (g.holder == user_uri or g.created_by == user_uri or g.holder in (None, '*'))]
    return grants

@pytest.yield_fixture
def permission(app, httpretty): # pylint: disable=redefined-outer-name
    Grant = collections.namedtuple(typename='Grant', field_names=[
        'created_by',
        'holder',
        'namespace',
        'object',
        'resource_name',
        'right',
        'uri'
    ])
    root = sepiida.permissions.CONFIG['PAO_ROOT']
    assert root, "You need to set up your PAO_ROOT in your app setup"

    class Permission():
        def __init__(self):
            self.creations  = {}
            self.deletions  = set()
            self.grants     = {}
            self.counters   = attrdict.AttrDict(
                DELETE      = 0,
                GET         = 0,
                LIST        = 0,
                POST        = 0,
            )
            httpretty.register_uri(
                httpretty.POST,
                urllib.parse.urljoin(root, '/permissions/'),
                body=self.capture_post,
            )
            httpretty.register_uri(
                httpretty.DELETE,
                re.compile(urllib.parse.urljoin(root, '/permissions/[\\-\\w]+/')),
                body=self.capture_delete,
            )
            httpretty.register_uri(
                httpretty.GET,
                urllib.parse.urljoin(root, '/permissions/'),
                body=self.capture_list,
            )
            httpretty.register_uri(
                httpretty.GET,
                re.compile(urllib.parse.urljoin(root, '/permissions/[\\-\\w]+/')),
                body=self.capture_get,
            )

        def matching_grants(self, filters, session):
            grants = [g for g in self.grants.values()]
            LOGGER.debug("Starting with %d permission grants available", len(grants))
            for f in filters:
                grants = [g for g in grants if getattr(g, f.name) in f.values]
                LOGGER.debug("%d permission grants left after filtering '%s in %s'", len(grants), f.name, f.values)
            grants = _filter_by_holder(grants, session)
            LOGGER.debug("Found %d grants matching search query %s", len(grants), filters)
            return grants

        def capture_get(self, request, uri, headers):
            self.counters['GET'] += 1
            headers['Content-Type'] = 'application/json'
            session = get_session_data(app, request)
            grant = self.grants.get(uri)
            grant = _filter_by_holder([grant], session) if grant else None
            grant = grant[0] if grant else None
            LOGGER.debug("Captured request for %s and found %s", uri, grant)
            if not grant:
                return 404, headers, ''
            body = {
                'uri'           : grant.uri,
                'holder'        : grant.holder,
                'namespace'     : grant.namespace,
                'object'        : grant.object,
                'resource_name' : grant.resource_name,
                'right'         : grant.right,
                'created_by'    : grant.created_by,
            }
            return 200, headers, JSON.dumps(body)

        def capture_list(self, request, _, headers):
            self.counters['LIST'] += 1
            headers['Content-Type'] = 'application/json'
            filters = _extract_filters(request)
            session = get_session_data(app, request)
            matching_grants = self.matching_grants(filters, session)
            body = {'resources': [{
                'uri'           : grant.uri,
                'holder'        : grant.holder,
                'namespace'     : grant.namespace,
                'object'        : grant.object,
                'resource_name' : grant.resource_name,
                'right'         : grant.right,
                'created_by'    : grant.created_by,
            } for grant in matching_grants]}
            LOGGER.debug("Captured request to list permissions and returning %d permission grants", len(matching_grants))
            return 200, headers, JSON.dumps(body)

        def capture_delete(self, _, uri, __):
            LOGGER.debug("Captured request to delete permission %s", uri)
            self.counters['DELETE'] += 1
            self.deletions.add(uri)
            if uri in self.grants:
                del self.grants[uri]
                LOGGER.debug("Removed %s from the list of available permission grants", uri)
                return 204, {}, ''
            return 404, {}, ''

        def capture_post(self, request, _, headers):
            self.counters['POST'] += 1
            privileged = _uses_privileged_auth(request.headers['Authorization'])
            session = _get_session(request.headers)
            body = JSON.loads(request.body.decode('utf-8'))
            body['privileged'] = privileged
            uuid = uuid4()
            location = urllib.parse.urljoin(root, '/permissions/{}/'.format(uuid))
            headers['Location'] = location
            self.creations[location] = body
            self.grants[location] = Grant(
                created_by      = session.get('user_uri', 'unknown'),
                holder          = body['holder'],
                namespace       = body['namespace'],
                resource_name   = body.get('resource_name'),
                right           = body['right'],
                object          = body['object'],
                uri             = location,
            )
            LOGGER.debug("Created new fake permission %s", self.grants[location])
            return 201, headers, ''

        def created(self, object_, holder, right, namespace, resource_name, privileged=False):
            expected = {
                'holder'        : holder,
                'namespace'     : namespace,
                'object'        : object_,
                'privileged'    : privileged,
                'resource_name' : resource_name,
                'right'         : right,
            }
            return expected in self.creations.values()

        def deleted(self, uri):
            return uri in self.deletions

        def grant(self, holder, namespace, right, object_, resource_name, created_by='unknown'):
            uuid = uuid4()
            holder = holder if holder is not None else '*'
            uri = urllib.parse.urljoin(root, '/permissions/{}/'.format(uuid))
            self.grants[uri] = Grant(
                created_by      = created_by,
                holder          = holder,
                namespace       = namespace,
                object          = object_,
                resource_name   = resource_name,
                right           = str(right),
                uri             = uri,
            )
            LOGGER.debug("Directly creating permission grant %s", self.grants[uri])
            return uri

    yield Permission()

def api(app):
    LOGGER.warning("You are using the api fixture. Use the app fixture instead")
    return app

@pytest.fixture(scope="session")
def external_cert():
    return """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqvZ8i1qxb5ijA6Z/oS1D
U9jZM4ZXRLEbErOt541cZC4/AbFjxRfc4vTNWux9JYIjRQ761XJnPNzRvOMnh2Dm
3s8O1MVC2QS4TqRz3ga2QjmqA9ISLmV3h01K9EqeCVlYLjR0yMpUaSJcwVD7kXJC
kATl4svjjpSlKNu/THd8Ybzq03WgMTB5SwysIWXO4jREMqvXGgxVGs54VLullTZy
psWvsm7GOX+wZfTiGk3YoWCI0xYBKWD5IRn5ykk1vt6Hr8m3qMLN8Hjn+70AgeqT
su4jOOKag9gxnvcEg6UAC9STWNLomCIjI39ZLGhg8wlSbE5o63s9CEizlNtiZLUX
ZwIDAQAB
-----END PUBLIC KEY-----"""

@pytest.fixture(scope="session")
def internal_cert():
    return """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAw6VojppAkc+FOC9kLLDt
pvDkE6lAJj1Af8sgzDuTlP9iVgUzC/qYIMupsMRUzbWP1LnYKGvILQxfna5py9hK
C/BwlYn8tZ1l8gfvjnJ86DrKwLfkiJImxQPAH4ZsIXeMdnOump71u62TiQJdnZtB
1pOjiDIsAQBIiCKJEZMwIYvmT8LUaazzTsf0BzvT1Vd5swUJTuJQBXV7sT5TvGXv
o9CwGoNyspr37/86BNQQou/xEIxVd27Hpshr/98ufv7oOVDKWQA+7XFANzoOf9Rs
24LINih3fnynoVzuTt/cNPHKZAKSccV2wz83B7lA03kqezV0ihJAiOfNmbstARl5
pwIDAQAB
-----END PUBLIC KEY-----"""

@pytest.fixture(scope="session")
def external_key():
    return """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAqvZ8i1qxb5ijA6Z/oS1DU9jZM4ZXRLEbErOt541cZC4/AbFj
xRfc4vTNWux9JYIjRQ761XJnPNzRvOMnh2Dm3s8O1MVC2QS4TqRz3ga2QjmqA9IS
LmV3h01K9EqeCVlYLjR0yMpUaSJcwVD7kXJCkATl4svjjpSlKNu/THd8Ybzq03Wg
MTB5SwysIWXO4jREMqvXGgxVGs54VLullTZypsWvsm7GOX+wZfTiGk3YoWCI0xYB
KWD5IRn5ykk1vt6Hr8m3qMLN8Hjn+70AgeqTsu4jOOKag9gxnvcEg6UAC9STWNLo
mCIjI39ZLGhg8wlSbE5o63s9CEizlNtiZLUXZwIDAQABAoIBADj1CaU7v+WYCqdK
rza5Z7blhedemHBwOL7QUd3VALT3m1IrETw2qQaL3GawZzk51BpL1VGLXc2vG8k8
PI0jwYb1oNFOLukyY1z/+QI9ZjdGEthXAmumrl3LaG9e9KvUskYif83tapXkNtbI
7icU1Aw7NYOLvfJgn22vWFpXbH768Af5Wizy+xEEDi2b96+y7XKCYqruOuM9aF/7
/P8zKLUSyNKfRp1fIBeGCwjJPXUjGFXnWiVu/hTOpo7faaIX4XqoRe/btnaAT6pD
eaR48I0Op4cn7qY1ocHqNnOVTbE9d4A+rfyhLn3zk15WAFIDfTVZi0Let5LCGYs8
/Y9aK3ECgYEA28o7klmMwWHbJCZ3Q1LJnFqs1He1AcNB+fSqXOHjiGoPEjUzz5xb
lND7OIUFrP6Bew7Zle/ra8tx9Qb7nbEustfv9Z1lfM3vYUO5ELD7MORgE5bp63cW
gnaR0Wt0uowQE1faa3zWSlDj1KWRMxg1Mlana61nBcbjZi/zBSlEBe0CgYEAxyDx
DbK3WHiHM8bBLaXxzlrM4nIeOk3QUInNvMktWYbL+qNhvA1rzLaNt5Km/3/gv5La
zBv4OCTxWmgbkeRZzLMnoJqHYcIaZXXfu0odu+RlWHg2weDVAdK76YMHMjeTb0Oc
zDvgqzkm7xVB/BIsDBh7G5TdzrMVYd+dDtYAaCMCgYA+jl/INr6uJ8j0kBIv0jdZ
ziEU1AFrwARePTnj99MH94/UkdnuREV4pMZr/shvxXxa5w4c881gv+XuZI9nAZAW
DQnaMXM6Q27XkyvwST8lWkrSKIjpoNqCRXcZUOlHUygcKUwcfcqMGlvOIVWjYkd5
zVoXdqI07be5VPppRKZ8vQKBgCx4Yt0YSHHtmOQrQwEaykG3bYI00iNbNWaHH/dF
Rmdz/yHeUvlYVfbF3ihdDAaLXHnsJgjnRivjtDLohR+zy4o3iGYJnKpsWtDF3k1J
ZBKOE0QKtM/fkjJyCZ1Asd65Iqf6hY3m4WnbvaIvMSlGNagN35BtUovS2rec5Mpn
aHfZAoGBANovb+N7Hw0I6VzZ3zC2O1fHvqcjvbsxtdqxhefgeLjE8E85veCHLSzY
VGlh2Jm4V9fYAJ+hWXquT8iZTUQ3fBgpi3c7zFpypqket8xBXSCK8zqiqoL5jPNs
Ja7Wtex7Q9fFHu7uGbz8Ab+7b6BDBbyCN4hZaCKREcenuplLSqXM
-----END RSA PRIVATE KEY-----"""

@pytest.fixture(scope="session")
def internal_key():
    return """-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEAw6VojppAkc+FOC9kLLDtpvDkE6lAJj1Af8sgzDuTlP9iVgUz
C/qYIMupsMRUzbWP1LnYKGvILQxfna5py9hKC/BwlYn8tZ1l8gfvjnJ86DrKwLfk
iJImxQPAH4ZsIXeMdnOump71u62TiQJdnZtB1pOjiDIsAQBIiCKJEZMwIYvmT8LU
aazzTsf0BzvT1Vd5swUJTuJQBXV7sT5TvGXvo9CwGoNyspr37/86BNQQou/xEIxV
d27Hpshr/98ufv7oOVDKWQA+7XFANzoOf9Rs24LINih3fnynoVzuTt/cNPHKZAKS
ccV2wz83B7lA03kqezV0ihJAiOfNmbstARl5pwIDAQABAoIBAHkZy6xpQop+v2FV
xFX9dj0dYq/g1bpVs7TmkPiZ7/IMWlwQf9ZsWPoD1pd6D1v9hHgSSQBMJu3reMvr
h8ULrlnRjH6jmO757H5x9xBfQX2l1paPvT/j52ePuL5KwGe+zg0L8gn3VvfCq03l
TvkdfxVI8bJ+C8ra2AqcBegBCYvZLVHg4jThgnbNq3FEqq0tSLgERdWLn1g3Fmal
wJpI3sRdDiRIASs4OUv/SYDpxbr2H+kdAHXidzijLtlF4guryxJqmnxe+4s2UKvB
rEe7ZH9xHeHWm5YeVLAya+7DqPsuLaxURnsSCY14oi9H/KAJwWtDr7mnT0U70Hnx
svKUJIECgYEA7D8WqtXc71zir2gbu3OK2SWVcuDk1abL1ZI3OyboZSqqPkS5dHna
uZGJpYXeNS7O4OZw5ettvozp6maG9CSx55j46cbo3Vl9niuyjdUKImHRPwl3hf8q
+gRyIFtYtHaMM2UzkVuK3nDOwsps/ACHajq/dbU510vkvyRRmEAVF8cCgYEA1AFC
r0185RvcZMZnCl+NjwNdMvyaVMv/zHq1aj6FBM4Eg+ATFkusnTRwXt3G5suvTQeb
a2OL7VosNPV9KZgljkzhRKb7rX6VpGEp04fLCLzhMtNUGpnGJ/Ls0rb12/WiJ5ID
LRBeiW6PAAJrAKfW/z0ib3tNdMiSlsV4CiGdTyECgYEA3pO91mwxgG7Bv8LVRfFg
4p8PQ7Fwx34jUu80DA3nK9Fbndj/5SYdFXJx/bm3FeIo1SknOudpePqoM8gu43xj
BLFR6mcV4925hTjkO854gtYn3z0bF+rFYdKod6W4WCXMh2uUfyGBH3umwU0YCwCw
lDwPQGXivd3qAM/F9CyD8ucCgYEA07Q+hxf19EOSHgARvUYV8g4F73hYFP1xfxu6
NVIhOt8PmzETXlxLDuDipZkJmkcj0uQZy28ot+gn5OqQBg0s06DqAshM4r9ZZ0Cv
p9Aea6dRqpNllPqh6hqnavPRJ8luF92y1jlWbh69JeFEQO9Zvp+p13Fls4zm9TBT
4qoWkIECgYEA1ZF0IVABttkUfYV+YG9JLcFi+eHbeCctlEnWZAisd2CYWKfY6rfI
XKmKPAguhan7QVFfvhXpT0RVRrJGRp65WJnwBNHn3e1FYCIz71J+wO1jMElrCQWk
gQi1+eorH63mzt6/HAZKVCnK3s2DvM87rDVY1GLCTrTNqcSICC9BvG4=
-----END RSA PRIVATE KEY-----"""

@pytest.fixture()
def pao_group(httpretty, external_cert, settings): # pylint: disable=redefined-outer-name
    group = {
        'uri'         : urllib.parse.urljoin(settings.USER_SERVICE, '/groups/{}/'.format(uuid4())),
        'name'        : 'The Sports Sesh',
        'description' : 'Sports talk show',
        'secret'      : external_cert,
    }

    httpretty.register_uri(
        httpretty.GET,
        group["uri"],
        status=200,
        body=JSON.dumps(group),
    )

    return group

@pytest.fixture
def config_override(app):
    @contextlib.contextmanager
    def _config_override(name, value): # pylint: disable=redefined-outer-name
        if name not in app.config:
            app.config[name] = value
            yield
            del app.config[name]
        else:
            previous = app.config[name]
            app.config[name] = value
            yield
            app.config[name] = previous
    return _config_override

def _uses_privileged_auth(authorization):
    if not authorization:
        return False
    parts = authorization.split(' ')
    decoded = base64.b64decode(parts[1])
    value = decoded.decode('utf-8')
    return value.split(':')[0] == 'api'

@pytest.yield_fixture
def backend_app(app):
    _backend_app = sepiida.backend.create('backend_app_fixture', testing=True, flask_app=app)
    yield _backend_app
    _backend_app.close()
    # this is needed to ensure we probably deregister our tasks on cleanup of the fixture
    # and prevent state bleed-over
    for instance in sepiida.backend.TaskProxy.instances:
        instance.celery_task = None
    sepiida.backend.create.application = None
    sepiida.backend.create.flask_app = None

@pytest.fixture
def mock_task_factory(mocker):
    def _factory(module_name):
        @sepiida.backend.task()
        def _inner(*args, **kwargs):
            _inner.ran = True
            _inner.task_args = args
            _inner.task_kwargs = kwargs
        _inner.ran = False
        _inner.task_args = None
        _inner.task_kwargs = None
        mocker.patch(module_name, side_effect=_inner)
        return _inner
    return _factory

@pytest.yield_fixture
def storage(settings, httpretty): # pylint: disable=redefined-outer-name
    MockFile = collections.namedtuple('MockFile', ('bucket', 'content', 'key', 'mimetype', 'uuid'))
    class MockStorage():
        def __init__(self):
            self.files = {}

            base = settings.STORAGE_SERVICE
            url = urllib.parse.urljoin(base, 'file/')
            httpretty.register_uri(
                httpretty.GET,
                url,
                body=self.capture_list,
            )
            httpretty.register_uri(
                httpretty.POST,
                url,
                body=self.capture_post_file,
            )
            pattern = re.compile(url + '[\\-\\w]+/')
            httpretty.register_uri(
                httpretty.GET,
                pattern,
                body=self.capture_get,
            )
            url = urllib.parse.urljoin(base, 'upload/')
            pattern = re.compile(url + '[\\-\\w]+/')
            httpretty.register_uri(
                httpretty.GET,
                pattern,
                body=self.capture_get_upload,
            )
            httpretty.register_uri(
                httpretty.PUT,
                pattern,
                body=self.capture_put_upload,
            )

        def store(self, key, bucket, content, mimetype, uuid=None):
            key = str(key)
            for uuid_, file_ in self.files.items():
                if file_.key == key and file_.bucket == bucket:
                    LOGGER.debug("Overwriting storage content for %s:%s", bucket, key)
                    uuid = uuid_
                    break
            uuid = uuid or uuid4()
            uuid = str(uuid)
            self.files[uuid] = MockFile(
                bucket      = bucket,
                content     = content,
                key         = key,
                mimetype    = mimetype,
                uuid        = uuid
            )
            return uuid

        def get(self, key):
            skey = str(key)
            for file_ in self.files.values():
                if skey == file_.key:
                    return self._to_resource(file_)
            return None

        @staticmethod
        def _to_resource(file_):
            return {
                'bucket'            : file_.bucket,
                'content'           : urllib.parse.urljoin(settings.STORAGE_SERVICE, 'upload/{}/'.format(file_.uuid)),
                'key'               : file_.key,
                'mimetype'          : file_.mimetype,
                'upload-location'   : urllib.parse.urljoin(settings.STORAGE_SERVICE, 'upload/{}/'.format(file_.uuid)),
                'uri'               : urllib.parse.urljoin(settings.STORAGE_SERVICE, 'file/{}/'.format(file_.uuid)),
            }

        def capture_get(self, _, uri, headers):
            uuid = uri.split('/')[-2]
            try:
                file_ = self.files[uuid]
                return 200, headers, JSON.dumps(self._to_resource(file_))
            except KeyError:
                return 404, headers, ''

        def capture_list(self, request, _, headers):
            headers['Content-Type'] = 'application/json'
            filters = _extract_filters(request)
            files = self.files.values()
            for filter_ in filters:
                files = [f for f in files if getattr(f, filter_.name) in filter_.values]
            body = {'resources' : [self._to_resource(file_) for file_ in files]}
            return 200, headers, JSON.dumps(body)

        def capture_post_file(self, request, _, headers):
            body = JSON.loads(request.body.decode('utf-8'))
            uuid = self.store(
                key         = body['key'],
                bucket      = body['bucket'],
                content     = None,
                mimetype    = None,
            )
            headers['Location'] = urllib.parse.urljoin(settings.STORAGE_SERVICE, 'file/{}/'.format(uuid))
            headers['Upload-Location'] = urllib.parse.urljoin(settings.STORAGE_SERVICE, 'upload/{}/'.format(uuid))
            LOGGER.debug("Captured POST of file %s with headers %s", self.files[uuid], headers.items())
            return 201, headers, ''

        def capture_get_upload(self, _, uri, headers):
            uuid = uri.split('/')[-2]
            file_ = self.files[uuid]
            LOGGER.debug("Captured GET of content %s which returned %s", uri, file_)
            if file_.content is None:
                return 404, headers, 'not here bro'
            return 200, headers, file_.content

        def capture_put_upload(self, request, uri, headers):
            uuid = uri.split('/')[-2]
            file_ = self.files[uuid]
            self.store(
                key         = file_.key,
                bucket      = file_.bucket,
                content     = request.body,
                mimetype    = request.headers.get('Content-Type'),
                uuid        = file_.uuid,
            )
            LOGGER.debug("Captured PUT of file content of len %d to %s", len(request.body), uri)
            return 204, headers, ''

    storage_ = MockStorage()
    yield storage_

@pytest.fixture
def disable_session_reuse():
    @contextlib.contextmanager
    def _disable_session_reuse():
        privileged_session_reuse = sepiida.requests.privileged_session.reuse
        user_session_reuse = sepiida.requests.user_session.reuse
        sepiida.requests.privileged_session.reuse = False
        sepiida.requests.user_session.reuse = False
        yield
        sepiida.requests.privileged_session.reuse = privileged_session_reuse
        sepiida.requests.user_session.reuse = user_session_reuse
    return _disable_session_reuse

@pytest.yield_fixture
def fakeenv():
    original_env = copy.deepcopy(os.environ)
    yield os.environ
    os.environ = copy.deepcopy(original_env)

@pytest.fixture(scope='session')
def settings_spec():
    return sepiida.environment.DEFAULT_SPEC

@pytest.fixture(scope='session')
def settings(external_key, settings_spec): # pylint: disable=redefined-outer-name
    results = sepiida.environment.parse(settings_spec)
    results['SEPIIDA_JWT_KEY'] = external_key
    return results
