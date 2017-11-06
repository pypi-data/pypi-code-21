import hashlib

import datetime

import jwt

from kck.lib.config import kck_config_lookup
from kck.lib.exceptions import AuthTokenInvalid, AuthTokenExpired

authed_userid = None
try:
    use_auth = kck_config_lookup("kck", "enable_auth")
except KeyError:
    use_auth = False


class KCKAuth(object):

    auth_secret = kck_config_lookup("auth", "secret") if use_auth else None
    password_hash_salt = kck_config_lookup("auth", "password_hash_salt") if use_auth else None

    def __init__(self, auth_dict):
        self.auth_dict = auth_dict

    def gen_password_hash(self, passwd):
        salt = self.password_hash_salt.encode("utf-8")
        salted_passwd = salt+passwd.encode("utf-8") if type(passwd) is str else salt+passwd
        return hashlib.md5(salted_passwd).hexdigest()

    def type(self):
        return self.auth_dict["type"]

    def userid_to_authtoken(self, user_id):
        currtime = datetime.datetime.utcnow()
        return jwt.encode(
            {
                'exp': currtime + datetime.timedelta(days=0, seconds=5),
                'iat': currtime,
                'sub': user_id
            },
            self.auth_secret,
            algorithm='HS256'
        )

    def authtoken_to_userid(self, token):
        try:
            return jwt.decode(
                token,
                self.auth_secret
            )['sub']
        except jwt.ExpiredSignatureError:
            raise AuthTokenExpired(token)
        except jwt.InvalidTokenError:
            raise AuthTokenInvalid(token)

    def authed_userid(self, userid=None):
        global authed_userid
        if userid is not None:
            authed_userid = userid
        return authed_userid