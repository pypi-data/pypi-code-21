import datetime as dt
import dateutil.parser
import dateutil.tz
import json
import logging
import os
import urllib
import requests
import requests_unixsocket
requests_unixsocket.monkeypatch()
import pystache

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA

from aalam_common.redisdb import redis_conn, baseapp_redisify_name
from aalam_common.config import cfg


def _sign_and_send(prefix, header_key, method, hostname, url,
                   scheme="http", **kwargs):
    if scheme == "http+unix":
        ses = requests_unixsocket.Session()
        req = getattr(ses, method.lower())
        hostname = hostname.replace("/", "%2F")
    else:
        req = getattr(requests, method.lower())

    _url = url
    params = kwargs.pop('params', None)
    message = prefix + "#" + url
    if params:
        enc_params = urllib.urlencode(params)
        _url = url + "?" + enc_params
        message = message + "?" + "&".join(
            ["%s=%s" % (x, params[x]) for x in params.keys()])

    uri = "%(scheme)s://%(hostname)s%(url)s" % {
        "hostname": hostname,
        "url": _url,
        "scheme": scheme
    }
    # add auth header
    key = RSA.importKey(open(cfg.CONF.privkey).read())
    h = SHA.new()
    h.update(message)
    signer = PKCS1_PSS.new(key)
    signature = ''.join(signer.sign(h).encode("base64").split('\n'))
    x_auth_signature = prefix + ";" + signature

    new_dict = {}
    if 'headers' in kwargs:
        h = kwargs['headers']
    else:
        new_dict['headers'] = {}
        h = new_dict['headers']

    h[header_key] = x_auth_signature

    json_content = kwargs.pop("json", None)
    if json_content is not None:
        kwargs.pop("data", None)
        new_dict["data"] = json.dumps(json_content)
        h['Content-Type'] = "application/json"
    kwargs.update(new_dict)

    return req(uri, **kwargs)


def request_central_server(method, url, **kwargs):
    return _sign_and_send(cfg.CONF.bizcode,
                          'X-Auth-Signature',
                          method,
                          cfg.CONF.central_server,
                          url, **kwargs)


def request_apps_server(method, url, **kwargs):
    return _sign_and_send(cfg.CONF.bizcode,
                          'X-Auth-Signature',
                          method,
                          cfg.CONF.apps_server,
                          url, **kwargs)


def request_local_server(method, url, **kwargs):
    if "user" in kwargs:
        prefix = os.path.join(
            cfg.CONF.app_provider_code, cfg.CONF.app_code, kwargs.pop('user'))
    else:
        prefix = os.path.join(cfg.CONF.app_provider_code, cfg.CONF.app_code)
    return _sign_and_send(
        prefix,
        'X-Auth-Internal',
        method,
        "127.0.0.1",
        url, **kwargs)


def deserialize_json_response(resp):
    if resp.status_code < 200 or resp.status_code > 299:
        return None

    if 'content-type' not in resp.headers or \
       "application/json" not in resp.headers['content-type']:
        return None

    return resp.json()


def mandatory_dataset(param):
    return "(*)" + param


class DateTimeRFC7231(object):
    pattern = "%a, %d %b %Y %H:%M:%S %Z"

    @staticmethod
    def encode(timestamp):
        return timestamp.strftime(DateTimeRFC7231.pattern)

    @staticmethod
    def decode(string):
        return dt.strptime(string, DateTimeRFC7231.pattern)


class datetime(object):
    UTC = dateutil.tz.gettz('UTC')
    USER_ZONE = None
    DATE_PATTERN = None

    @staticmethod
    def userzone():
        if datetime.USER_ZONE is None:
            try:
                datetime.USER_ZONE = dateutil.tz.gettz(
                    Settings.get("timezone", "aalam", "base"))
            except:
                datetime.USER_ZONE = datetime.UTC

        return datetime.USER_ZONE

    def validator(func):
        def _wrapper(dtime):
            datetime.get_default_pattern()
            if isinstance(dtime, str) or isinstance(dtime, unicode):
                day_first = datetime.DATE_PATTERN.index('%d') < \
                    datetime.DATE_PATTERN.index('%m')
                dtime = dateutil.parser.parse(dtime, dayfirst=day_first)
            elif not isinstance(dtime, dt.datetime):
                raise ValueError("Input should either be string or datetime")
            elif dtime.tzinfo is None:
                raise ValueError("Datetime object cannot be naive")

            return func(dtime)

        return _wrapper

    @staticmethod
    def utcnow():
        return dt.datetime.utcnow().replace(tzinfo=datetime.UTC)

    @staticmethod
    @validator
    def to_db(dtime):
        if dtime.tzname() != 'UTC':
            dtime = dtime.astimezone(datetime.UTC)

        return dtime.replace(tzinfo=None)

    @staticmethod
    def from_db(dtime):
        return dtime.replace(tzinfo=datetime.UTC) if dtime else None

    @staticmethod
    def get_default_pattern():
        if datetime.DATE_PATTERN is None:
            try:
                setting = Settings.get("date_format", "aalam", "base")
                datetime.DATE_PATTERN = setting.replace(
                    "YYYY", "%Y").replace(
                    "MM", "%m").replace(
                    "DD", "%d")
            except:
                datetime.DATE_PATTERN = "%d-%m-%Y"

        return datetime.DATE_PATTERN

    @staticmethod
    @validator
    def to_user(dtime, pattern=None):
        if dtime.tzinfo != datetime.userzone():
            dtime = dtime.astimezone(datetime.userzone())

        if not pattern:
            pattern = datetime.get_default_pattern() + "T%H:%M:%S"
        return dtime.strftime(pattern)

    @staticmethod
    @validator
    def from_user(dtime):
        # parsing would have been done by the validator
        return dtime.replace(tzinfo=datetime.userzone())


class date(dt.date):
    DATE_PATTERN = None

    @staticmethod
    def _user_format():
        if date.DATE_PATTERN is None:
            try:
                setting = Settings.get("date_format", "aalam", "base")
                date.DATE_PATTERN = setting.replace(
                    "YYYY", "%Y").replace(
                    "MM", "%m").replace(
                    "DD", "%d")
            except:
                date.DATE_PATTERN = "%d-%m-%Y"

        return date.DATE_PATTERN

    @staticmethod
    def from_user(ddate):
        if isinstance(ddate, str) or isinstance(ddate, unicode):
            return dt.datetime.strptime(ddate, date._user_format()).date()

    @staticmethod
    def to_user(ddate):
        return ddate.strftime(date._user_format())


class AppCache(object):
    @staticmethod
    def get(app_class=None, provider=None, app=None, detail=False):
        key_name = baseapp_redisify_name(
            "app-%s" %
            (app_class if app_class else "/".join([provider, app])))

        try:
            if detail:
                keys = ["id", "version", "app_name", "provider_name",
                        "app_code", "provider_code"]
                values = redis_conn.hmget(key_name, keys)
                ret = dict(zip(keys, values))
                ret['id'] = int(ret['id'])
                return ret
            else:
                return int(redis_conn.hget(key_name, 'id'))
        except:
            return None


def generate_RSA(bits=1024):
    new_key = RSA.generate(bits)
    public_key = new_key.publickey().exportKey("PEM")
    private_key = new_key.exportKey("PEM")
    return private_key, public_key


class mustachify(object):
    def __init__(self, template_path, **options):
        self._path = template_path
        self._options = options
        if "partial_files" in options:
            if 'partials' not in self._options:
                self._options['partials'] = {}

            files = self._options.pop('partial_files')
            for (k, v) in files.iteritems():
                with open(v) as fd:
                    self._options['partials'][k] = fd.read()

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            return pystache.Renderer(**self._options).render_path(
                self._path, ret)

        return wrapper


class Settings(object):
    @classmethod
    def get(cls, key, provider, app):
        code = '/'.join([provider, app, key])
        value = redis_conn.get(baseapp_redisify_name(code))
        if not value:
            resp = request_local_server(
                "GET",
                "/aalam/base/setting/%s/%s/%s" % (provider, app, key))
            if resp.status_code != 200:
                logging.error("Unable to find setting %s/%s/%s" % (
                    provider, app, key))
                return None

            data = resp.json()
            value = data['value']

        return value
