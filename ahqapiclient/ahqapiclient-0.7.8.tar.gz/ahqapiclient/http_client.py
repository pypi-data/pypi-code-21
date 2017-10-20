# -*- coding: utf-8 -*-

from base64 import b64encode
from datetime import datetime
from hashlib import sha1, md5
import hmac
from json import (
    dumps as json_dumps,
    loads as json_loads
)
import logging
from os import fsync
import sys
from zlib import adler32

from builtins import object
from future import standard_library
from requests import Session, Request
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, Timeout
from requests.utils import guess_json_utf

from urllib.parse import unquote_plus
from urllib.parse import urlencode
from urllib.parse import urlparse
standard_library.install_aliases()



def write_pem(pem, content):
    write = False

    try:
        with open(pem):
            pass
    except IOError:
        write = True

    if write:
        with open(pem, 'w') as f:
            f.write(content)
            f.flush()
            fsync(f)


def get_tls_certs(endpoint, tmp_path='/tmp'):
    sum_ca = adler32(endpoint['auth_options']['ca']) & 0xffffffff
    sum_cert = adler32(endpoint['auth_options']['cert']) & 0xffffffff

    ca_file = '%s/ca-%s.%s.pem' % (tmp_path, endpoint['id'], sum_ca)
    cert_file = '%s/cert-%s.%s.pem' % (tmp_path, endpoint['id'], sum_cert)

    write_pem(ca_file, endpoint['auth_options']['ca'])
    write_pem(cert_file, endpoint['auth_options']['cert'])

    return (ca_file, cert_file)


def response_to_json(response):
    '''Returns the json-encoded content of a response, if any.'''

    if not response.encoding and len(response.content) > 3:
        # No encoding set. JSON RFC 4627 section 3 states we should expect
        # UTF-8, -16 or -32. Detect which one to use; If the detection or
        # decoding fails, fall back to `self.text` (using charset to make
        # a best guess).
        encoding = guess_json_utf(response.content)

        if encoding is not None:
            resp = response.content.decode(encoding)
            return json_loads(resp)

    resp = response.text or response.content
    return json_loads(resp)


class HTTPException(Exception):

    def __init__(self, text, status_code):
        Exception.__init__(self, text)
        self.status_code = status_code
        self.text = text

    def __str__(self):
        return str(self.__dict__)


class HTTPClient(object):

    DEFAULT_ACCEPT = 'application/json'
    DEFAULT_CONTENT_TYPE = 'application/json'
    DEFAULT_USER_AGENT = 'abusehq-api-client/0.4.0'  # change me to version.txt

    def __init__(self, default_endpoint, timeout=60.0):
        self.default_endpoint = default_endpoint
        self.timeout = timeout
        self.__session = Session()
        self.__session.mount('https://', HTTPAdapter(max_retries=2, pool_connections=100, pool_maxsize=100))
        self.log = logging.getLogger(self.__class__.__name__)

    def __set_default_headers(self, request):
        if 'Accept' not in request.headers:
            request.headers['Accept'] = self.DEFAULT_ACCEPT

        if 'Content-Type' not in request.headers:
            request.headers['Content-Type'] = self.DEFAULT_CONTENT_TYPE

        if 'User-Agent' not in request.headers:
            request.headers['User-Agent'] = self.DEFAULT_USER_AGENT

        return request

    def __set_auth(self, request, endpoint):
        auth_method = endpoint['auth_method']
        auth_options = None

        if 'auth_options' in endpoint:
            auth_options = endpoint['auth_options']

        if auth_method == 'NONE':
            pass
        elif auth_method == 'JWT':
            request.headers['Authorization'] = 'Bearer %s' % auth_options['token']
        elif auth_method == 'HTTP':
            request.headers['Authorization'] = 'Basic %s' % b64encode(
                '%s:%s' % (auth_options['user'], auth_options['password'])
            )
        elif auth_method == 'HMAC' or auth_method == 'INTERNAL':
            uid_as_string = str(auth_options['user'])
            key = str(auth_options['key'])
            uid = uid_as_string
            if sys.version_info[0] > 2:
                key = bytes(key, "ascii")
                uid = bytes(uid, "ascii")
            request.headers['X-API-KEY'] = '%s:%s' % (
                uid_as_string, hmac.new(key, uid, sha1).hexdigest()
            )
        elif auth_method == 'NEW':
            request.headers['X-Date'] = datetime.utcnow().isoformat()
            request.headers['X-Entropy'] = datetime.utcnow().strftime('%s')

            parsed_url = urlparse(request.url)

            content_md5 = md5()
            content_md5.update(request.data or '')

            string_to_sign = '%s\n%s\n' % (
                request.method, content_md5.hexdigest()
            )

            if 'Content-Type' in request.headers:
                string_to_sign += request.headers['Content-Type'] + '\n'
            else:
                string_to_sign += '\n'

            string_to_sign += request.headers['X-Date'] + '\n'
            string_to_sign += request.headers['X-Entropy'] + '\n'
            string_to_sign += parsed_url.path + '\n'

            params = {}
            for key, val in request.params.items():
                if val is not None:
                    params[key] = val

            string_to_sign += unquote_plus(urlencode(request.params))
            # string_to_sign += unquote_plus(urlencode(params))
            # print string_to_sign

            h = hmac.new(auth_options['key'], string_to_sign, sha1)
            signature = b64encode(h.digest())

            request.headers['Authorization'] = 'HMAC %s:%s' %\
                (auth_options['user'], signature)
        elif auth_method == 'TLS':
            (ca_file, cert_file) = get_tls_certs(endpoint)
            request.verify = ca_file
            request.cert = (cert_file, '/var/local/abusehq-backend/ahq.key')

        return request

    def __send(self, request, endpoint, raw):
        request = self.__set_default_headers(request)
        request = self.__set_auth(request, endpoint)
        max_timeout_retries = 2
        max_reset_by_peer_retries = 2
        response = None

        kwargs = {'timeout': self.timeout}

        for attr in ('verify', 'cert'):
            if hasattr(request, attr):
                kwargs[attr] = getattr(request, attr)

        if 'verify' not in kwargs:
            kwargs['verify'] = False

        while 1:
            try:
                response = self.__session.send(
                    request.prepare(), **kwargs
                )
            except ConnectionError as e:
                msg = str(e)

                if 'Connection reset by peer' in msg:
                    max_reset_by_peer_retries -= 1

                    self.log.warning(
                        'Connection reset by peer. Retries left %s' %
                        max_reset_by_peer_retries
                    )
                    continue
                else:
                    raise HTTPException(
                        '%s. (%s)' % (e, request.url), -1
                    )
            except Timeout as e:
                if max_timeout_retries:
                    max_timeout_retries -= 1
                    self.log.warning(
                        'Connection timeout. Retries left %s' %
                        max_timeout_retries
                    )
                else:
                    raise HTTPException(
                        '%s. (%s)' % (e, request.url), 0
                    )
            else:
                break

        if raw:
            return response
        else:
            if response.status_code >= 400:
                raise HTTPException(
                    '%s. (%s)' % (response.text, request.url),
                    response.status_code
                )

            return response_to_json(response)

    def __url(self, endpoint, path):
        return '%s%s' % (endpoint['url'].rstrip('/'), path)

    def _dumps(self, data):
        if data:
            try:
                data = json_dumps(data)
            except UnicodeDecodeError as e:
                raise RuntimeError('Failed to decode unicode', e)

        return data

    def request(self, method, path, params, data, endpoint, headers, raw):
        if not endpoint:
            endpoint = self.default_endpoint

        r = Request(
            method=method,
            url=self.__url(endpoint, path),
            params=params,
            data=data,
            headers=headers,
        )

        return self.__send(r, endpoint, raw)

    def get(self, path, params=None, endpoint=None, headers=None, raw=False):
        return self.request(
            'GET', path, params, None, endpoint, headers, raw
        )

    def post(self, path, params=None, data=None, endpoint=None, headers=None,
             raw=False):
        if data:
            data = self._dumps(data)

        return self.request(
            'POST', path, params, data, endpoint, headers, raw
        )

    def put(self, path, params=None, data=None, endpoint=None, headers=None,
            raw=False):
        if data:
            data = self._dumps(data)

        return self.request(
            'PUT', path, params, data, endpoint, headers, raw
        )

    def delete(self, path, params=None, endpoint=None, headers=None,
               raw=False):
        return self.request(
            r'DELETE', path, params, None, endpoint, headers, raw
        )

