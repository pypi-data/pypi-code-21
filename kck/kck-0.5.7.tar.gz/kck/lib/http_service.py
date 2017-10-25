import json
import datetime
import traceback

import tornado.web

from urllib.parse import urlparse, parse_qs
from tornado.options import define, options, parse_command_line
from kck.lib.exceptions import KCKKeyNotSetException, AuthHeaderNotPresent, AuthLoginUnknownUser
from kck.lib.kck_auth import KCKAuth
from .config import kck_config_lookup

define("port", default=8001, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")

try:
    use_auth = kck_config_lookup("kck", "enable_auth")
except KeyError:
    use_auth = False

auth_obj = KCKAuth(auth_dict=kck_config_lookup("auth")) if use_auth else KCKAuth(auth_dict=None)


def authed_handler_method(f):
    def wrapper(*args):
        self = args[0]

        if use_auth:
            auth_token = self.request.headers.get('Authorization')

            if not auth_token:
                raise AuthHeaderNotPresent

            auth_obj.authed_userid(auth_obj.authtoken_to_userid(auth_token))

        return f(*args)
    return wrapper


def encode_exceptions_in_response(f):
    def wrapper(*args):
        self = args[0]

        try:
            return f(*args)
        except Exception as e:

            try:
                ret = e.failure_info_dict()
            except AttributeError:
                ret = dict(
                    error=dict(
                        name=e.__class__.__name__,
                        args=e.args,
                        traceback=traceback.format_tb(e.__traceback__),
                    )
                )

            ret["success"] = False
            self.write(ret)

    return wrapper


class FrameworkWebServiceHandler(tornado.web.RequestHandler):
    keysep = "/"
    def request_body_as_dict(self):
        data = {}
        for k, v in parse_qs(self.request.body).items():
            data[str(k, 'utf-8')] = str(v[0], 'utf-8')
        return data


class CreateHandler(FrameworkWebServiceHandler):

    @encode_exceptions_in_response
    @authed_handler_method
    def put(self, key):
        from kck.lib.kck_data import KCKData
        self.write(KCKData.get_instance().update(key, self.request_body_as_dict()))


class UpdateHandler(FrameworkWebServiceHandler):

    @encode_exceptions_in_response
    @authed_handler_method
    def post(self, key):
        from kck.lib.kck_data import KCKData
        req_body = self.request_body_as_dict()
        result = KCKData.get_instance().update(key, req_body)
        self.write(result)


class FetchHandler(FrameworkWebServiceHandler):
    @encode_exceptions_in_response
    @authed_handler_method
    def get(self, key):

        from kck.lib.kck_cache import KCKCache
        r = KCKCache.get_instance().get(key)
        r["modified"] = str(r["modified"]) if type(r["modified"]) is datetime.datetime else r["modified"]
        self.write(r)


if use_auth:
    class LoginHandler(FrameworkWebServiceHandler):

        @encode_exceptions_in_response
        def post(self, username):
            global use_auth
            global auth_obj
            http_server_instance = KCKHTTPServer.get_instance()
            # auth_obj = _http_server_instance.auth_obj
            passwd = self.request.arguments["password"][0]
            passwd_hash = auth_obj.gen_password_hash(passwd) if use_auth else None

            authkey_template = kck_config_lookup("auth", "auth_user") if use_auth else None
            authkey_elements = authkey_template.split(self.keysep) if authkey_template is not None else None
            key_list = []
            for key_element in authkey_elements:
                if key_element[0] == ":":
                    local_vars = locals()
                    key_list.append(local_vars[key_element[1:]])
                else:
                    key_list.append(key_element)

            # req = self.request
            key = self.keysep.join(key_list)

            from kck.lib.kck_cache import KCKCache
            try:
                r = KCKCache.get_instance().get(key)
            except KCKKeyNotSetException:
                raise AuthLoginUnknownUser(username=username)

            self.write(json.dumps({"success": True, "auth_token": auth_obj.userid_to_authtoken(r["value"]).decode()}))


    class LogoutHandler(FrameworkWebServiceHandler):

        @encode_exceptions_in_response
        @authed_handler_method
        def get(self, username):
            r = self.request


_http_server_instance = None

class KCKHTTPServer(tornado.web.Application):

    # auth_obj = None

    @classmethod
    def get_instance(cls):
        global _http_server_instance

        if _http_server_instance is None:
            _http_server_instance = cls()

        return _http_server_instance

    def __init__(self):
        global use_auth
        routes = [
            (r"/create/(.*)", CreateHandler),
            (r"/update/(.*)", UpdateHandler),
            (r"/fetch/(.*)", FetchHandler),
        ]

        # try:
        #     self.use_auth = kck_config_lookup("kck", "enable_auth")
        # except KeyError:
        #     pass

        if use_auth:
            # self.auth_obj = KCKAuth(auth_dict=kck_config_lookup("auth"))
            # print("adding auth routes")
            routes.append((r"/login/(.*)", LoginHandler),)
            routes.append((r"/logout/(.*)", LogoutHandler), )
        # else:
        #     self.auth_obj = KCKAuth(auth_dict=None)


        super(KCKHTTPServer, self).__init__(
            routes,
            debug=options.debug,
        )

