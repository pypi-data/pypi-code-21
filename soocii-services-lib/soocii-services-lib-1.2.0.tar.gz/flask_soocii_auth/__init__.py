"""Flask extension for Soocii's access token authentication

Reference: http://flask.pocoo.org/docs/0.12/extensiondev/#extension-dev
"""
import binascii
import os
from functools import partial

from flask import g, request, current_app, abort, jsonify, make_response

from flask_soocii_auth import users, exceptions
from soocii_services_lib import auth

__all__ = ('SoociiAuthenticator',)


class SoociiAuthenticator:
    """ Access token authenticator for Soocii

    This authenticator will decode and validate access token.
    Decoded token will be stored in `g.access_token` and encoded access token will be stored in `g.raw_access_token`.
    This Authenticator will also store user info in `g.user`.
    You can refer to `flask_soocii_auth.users` for more information.
    """

    def __init__(self, app, is_safe_request_func=None):
        """Construct a Soocii Authenticator

        :param app: Flask app instance.
        :param is_safe_request_func: Pass a function to this argument. This function will be invoke when processing
                                     request without token. Return `True` if the request is valid without token.
                                     Otherwise, return False. SoociiAuthenticator will abort the request with
                                     HTTP 401 while request without token and `is_safe_request_func` return `False`.
        """

        self._validate_env_vars()

        self.app = app
        self.is_safe_req_func = is_safe_request_func

        self._register_hooks()

    def _validate_env_vars(self):
        try:
            binascii.unhexlify(os.getenv('ACCESS_TOKEN_SECRET'))
            binascii.unhexlify(os.getenv('REFRESH_TOKEN_SECRET'))
        except binascii.Error:
            raise exceptions.InvalidTokenSecretError

    def _register_hooks(self):
        self.app.before_request(partial(SoociiAuthenticator.validate_token, self.is_safe_req_func))
        self.app.before_request(SoociiAuthenticator.authorize_user)
        pass

    @staticmethod
    def validate_token(is_safe_request_func=None):
        def abort_json_resp(status, data):
            abort(status, response=make_response(jsonify(data), status))

        try:
            # Try to get request.args first instead of get request.json first.
            # If we try to get request.json before request.args, Flask may return 400 BAD REQUEST.
            # The reason is client may send HTTP GET with content-type: application/json but actual data is store in
            # query string. (GET me/follower API is an example which we encounter)
            # When Flask check mine type and found mine type is json, Flask will try to decode json and fail,
            # then Flask will response 400.
            raw_token = None
            if request.headers.get('Authorization'):
                raw_token = request.headers.get('Authorization').replace('Bearer ', '')
            elif 'access_token' in request.args:
                raw_token = request.args.get('access_token')
            elif request.is_json and 'access_token' in request.get_json(cache=True):
                raw_token = request.get_json()['access_token']
            elif request.form != '' and 'access_token' in request.form:
                raw_token = request.form['access_token']

            if raw_token is None:
                raise UnboundLocalError

            g.access_token = auth.decode_access_token(raw_token)
            g.raw_access_token = raw_token

        except auth.AccessTokenValidationFail:
            # :except AccessTokenValidationFail: raises when token denied, including expired, illegal token.
            current_app.logger.warning("AccessTokenValidationFail")
            abort_json_resp(401, {"errors": ['Invalid access_token']})
        except ValueError:
            # :except ValueError: raises when token format illegal, such as incorrect length.
            current_app.logger.warning("ValueError")
            abort_json_resp(401, {"errors": ['Illegal access_token']})
        except UnboundLocalError:
            # :except UnboundLocalError: raises when request without token.
            if is_safe_request_func and is_safe_request_func(request):
                pass
            else:
                current_app.logger.info("UnboundLocalError")
                abort_json_resp(401, {"errors": ['Please provide access token.']})
        except Exception as e:
            current_app.logger.error("Unknown exception: {}".format(e))

        current_app.logger.info(
            "{req.method} {req.path}. "
            "access_token: {token}. ".format(
                token=g.access_token if hasattr(g, 'access_token') else None,
                req=request
            )
        )

    @staticmethod
    def authorize_user():
        if not hasattr(g, 'access_token'):
            g.user = users.AnonymousUser()
            return

        if g.access_token['uid'] == '':
            g.user = users.BackstageUser()
            return

        g.user = users.User()
