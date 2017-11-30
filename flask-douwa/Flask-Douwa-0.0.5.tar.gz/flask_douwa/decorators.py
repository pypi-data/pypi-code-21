import json
from datetime import datetime, timedelta
from werkzeug.exceptions import Forbidden

from functools import wraps
from flask import request, g, abort
from flask_douwa import redis
from flask_douwa import reqparse

TOKEN_PREFIX = "douwa:token:"
TOKEN_EXPIRES = 3600
PERMISSION_PREFIX = "duowa:permission:"
TOKEN = "SX0L1WOV9MEwOBYTxSLA8qtLibvpPYGK4sPppoDyWs0="


def authorization(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        prefix = TOKEN_PREFIX
        ttl = TOKEN_EXPIRES

        user = None
        if 'Authorization' in request.headers:
            token = request.headers.get('Authorization')[7:]
        else:
            parserd = reqparse.RequestParser()
            parserd.add_argument('access_token', "token", type=str)
            args = parserd.parse_args()
            if "access_token" in args:
                token = args["access_token"]
            else:
                token = None

        if token:
            key = prefix + token
            user_cached = redis.get(key)
            if user_cached:
                try:
                    user = json.loads(user_cached)
                except Exception as e:
                    user = None
                    raise Exception(e)
        if not user:
            try:
                abort(401)
            except Exception as e:
                e.data = "用户没有登录!"
                raise
        if token != TOKEN:
            expired = redis.ttl(key)
            if expired:
                redis.expire(key, ttl)

        g.user = user
        return f(*args, **kwargs)

    return decorated_function


def permission(name):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            userrole = set(g.user["roles"])
            key = PERMISSION_PREFIX + name
            dd = redis.smembers(key)
            if userrole & dd:
                return func(*args, **kwargs)
            else:
                raise Forbidden("没有操作权限!")
        return inner
    return wrapper
