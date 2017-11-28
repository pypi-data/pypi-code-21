from base64 import b64decode
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA
from ecdsa import VerifyingKey
from ecdsa.util import sigdecode_der
import binascii
import os
import logging
import webob.exc
import aalam_common.wsgi as wsgi
import aalam_common.utils as zutils
from aalam_common.config import cfg


AUTH_COOKIE_NAME = "auth"  # This is the cookie set by central auth server
ANONYMOUS_USERNAME = "Anonymous"
ANONYMOUS_EMAIL = "anonymous"


class Auth(wsgi.Middleware):
    def __init__(self, app):
        super(Auth, self).__init__(app)

    def _handle_token_auth(self, request):
        token = request.headers.get("X-Auth-Token")
        if not token:
            return False

        url = "/aalam/base/tokenauth/app/**/token/%s" % token
        titem = zutils.deserialize_json_response(
            zutils.request_local_server("GET", url))

        if not titem:
            logging.warn("Got an invalid token")
            raise webob.exc.HTTPUnauthorized()

        expiry = zutils.datetime.from_user(titem['expiry'])
        if expiry < zutils.datetime.utcnow():
            logging.warn(
                "Got an expired token for app %s" % titem['app']['name'])
            raise webob.exc.HTTPUnauthorized()

        request.auth = titem['app']['id']
        return True

    def _verify_signature(self, key_file, header_value, request):
        (prefix, signature) = header_value.split(";")
        params = request.params
        if params:
            params = '&'.join(
                ["=".join([k, v]) for k, v in params.iteritems()])
            url = request.path + "?" + params
        else:
            url = request.path
        message = "#".join([prefix, url])
        pub_key = RSA.importKey(open(key_file, "r").read())
        auth_signer = PKCS1_PSS.new(pub_key)
        h = SHA.new()
        h.update(message)

        signature = b64decode(signature)
        return auth_signer.verify(h, signature), prefix

    def _validate_user_signature(self, path, email_id, ts, signature):
        try:
            with open(path, "r") as fd:
                vk = VerifyingKey.from_pem(fd.read())
                cookie_val_b = binascii.a2b_base64(signature)
                message = "#".join([email_id, ts])
                if (vk.verify(cookie_val_b, message, sigdecode=sigdecode_der)):
                    return True
                else:
                    raise webob.exc.HTTPUnauthorized()
        except:
            import traceback
            traceback.print_exc()
            raise webob.exc.HTTPUnauthorized()

    def _fetch_user_keys(self, email_id):
        payload = {'email_id': email_id}
        resp = zutils.request_local_server(
            "POST", "/aalam/base/central/userkey", params=payload)
        if resp.status_code != 200:
            return False

        return True

    def _handle_cookie_auth(self, request):
        auth_cookie = request.cookies.pop(AUTH_COOKIE_NAME, None)

        if auth_cookie:
            email_id, ts, signature = auth_cookie.split('#', 2)
            path = os.path.join(cfg.CONF.auth.userkeys_path,
                                "%s.pub" % email_id)
            if not os.path.exists(path) and \
                    not self._fetch_user_keys(email_id):
                return False

            if self._validate_user_signature(path, email_id,
                                             ts, signature):
                request.auth = {"email_id": email_id}
                return True

        return False

    def _handle_internal_auth(self, request):
        internal = request.headers.get("X-Auth-Internal", None)
        if internal:
            (prefix, signature) = internal.split(";")
            p = prefix.split("/")
            pubkey = os.path.join(
                os.path.dirname(cfg.CONF.pubkey),
                "%s_%s.pub" % (p[0], p[1]))
            (ret, prefix) = self._verify_signature(
                pubkey, internal, request)
            if not ret:
                raise webob.exc.HTTPUnauthorized()

            request.auth = {'internal': True,
                            'from': prefix}

            if len(p) > 2:
                email = p[2]
            else:
                email = get_app_email(p[0], p[1])

            request.auth['email_id'] = email

            return True

        return False

    def _handle_external_auth(self, request):
        signature = request.headers.get('X-Auth-Signature', None)
        if signature:
            prefix = signature[:signature.index(';')]
            ret = False
            if prefix == 'CENTRALPORTAL':
                (ret, _) = self._verify_signature(
                    cfg.CONF.auth.central_pubkey, signature, request)
            elif prefix.startswith('APPSPORTAL'):
                (ret, _) = self._verify_signature(
                    cfg.CONF.auth.apps_server_pubkey, signature, request)

            if not ret:
                raise webob.exc.HTTPUnauthorized()

            request.auth = {'external': True}
            if "/" in prefix:
                prefix, email = prefix.split("/")
                resp = zutils.request_local_server(
                    "GET",
                    "/aalam/base/users?fields=id&email=%s"
                    % email)
                if resp.status_code != 200:
                    raise webob.exc.HTTPUnauthorized()
                data = resp.json()
                user_id = data[0]

                request.auth['email_id'] = email
                request.auth['id'] = user_id

            request.auth['from'] = prefix
            return True

        return False

    def _handle_anonymous(self, request):
        # allow anonymous users, role module will manage it
        request.auth = {"email_id": ANONYMOUS_EMAIL}
        return None

    def pre(self, request):
        if self._handle_token_auth(request):
            pass
        elif self._handle_cookie_auth(request):
            pass
        elif self._handle_internal_auth(request):
            pass
        elif self._handle_external_auth(request):
            pass
        else:
            self._handle_anonymous(request)

        return None


class TestAuth(wsgi.Middleware):
    # This is used just for testing
    def pre(self, request):
        request.auth = {'email_id': 'user@test.test',
                        "internal": True,
                        "from": "aalam/xxxx"}


is_anonymous_user = lambda request: not request.auth or request.auth.get(
    "email_id", None) == ANONYMOUS_EMAIL


def deny_anonymous_user(request):
    if is_anonymous_user(request):
        raise webob.exc.HTTPForbidden(
            explanation="Forbidden for anonymous users")


def get_auth_user_id(request, deny_anon=True):
    auth = request.auth if hasattr(request, "auth") else None
    if is_anonymous_user(request) and deny_anon:
        raise webob.exc.HTTPForbidden(
            explanation="Forbidden for anonymous users")

    if is_anonymous_user(request):
        return (None, ANONYMOUS_EMAIL)

    id = email_id = None
    if 'email_id' in auth:
        email_id = auth['email_id']

    if 'id' in auth:
        id = auth['id']

    return (id, email_id)


def get_auth_user(request, deny_anon=True):
    (_, email_id) = get_auth_user_id(request)
    return email_id


def is_auth_internal(request):
    auth = request.auth if hasattr(request, "auth") else None
    if auth:
        if auth.get("internal", False):
            return auth.get("from")

    return False


def is_auth_external(request):
    auth = request.auth if hasattr(request, "auth") else None
    if auth:
        if auth.get("external", False):
            return auth.get("from")

    return False


def deny_external_source(request):
    if not is_auth_internal:
        raise webob.exc.HTTPNotFound()


def get_app_email(provider_code, app_code):
    return '_'.join([provider_code, app_code]) + "@%s" % cfg.CONF.hostname


def init_auth():
    pass
