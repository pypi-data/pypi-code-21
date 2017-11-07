# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

import sys
import hmac
import hashlib

from http.cookies import BaseCookie

from future.backports.urllib.parse import urlencode
from future.backports.urllib.parse import urlsplit
from future.backports.urllib.parse import urlunsplit
from future.backports.urllib.parse import parse_qs

from tcell_agent.config import CONFIGURATION


USE_PYTHON_2_HASH = (sys.version_info.major == 2 and hash("hash") == 7799588877615763652)


def ensure_str_or_unicode(encoding, value):
    if isinstance(value, bytes):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            return value.decode('ISO-8859-1')
    else:
        return value


def remove_trailing_slash(path):
    if path and path != "/":
        return path.rstrip("/")

    return path


def java_hash(s):
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000


def python_dependent_hash(s):
    if USE_PYTHON_2_HASH:
        return hash(s)
    else:
        return java_hash(s)


class SanitizeUtils(object):
    radius = 0

    @classmethod
    def hmac(cls, value):
        hmac_key = "hmac_key"
        if CONFIGURATION:
            if CONFIGURATION.hmac_key is not None:
                hmac_key = CONFIGURATION.hmac_key
            elif CONFIGURATION.app_id is not None:
                hmac_key = CONFIGURATION.app_id
        try:
            hmac_key_enc = bytes(hmac_key, "utf-8")
        except:
            hmac_key_enc = bytes(hmac_key)
        digest = hmac.new(hmac_key_enc, str(value).encode('utf-8'), hashlib.sha256).hexdigest()
        return digest

    @classmethod
    def hmac_half(cls, value):
        hmacd = cls.hmac(value)
        if hmacd and len(hmacd) > 32:
            hmacd = hmacd[0:32]
        return hmacd

    @classmethod
    def strip_query_string(cls, query_string):
        query_string_type = str(type(query_string))

        # use utf-8 decoding to change it to unicode in python2
        if query_string_type.startswith("<type 'str'"):
            query_string = query_string.decode('utf-8')

        query_params = parse_qs(query_string)

        for param_name, param_values in query_params.items():
            new_param_values = []
            for _ in param_values:
                new_param_values.append("")
            query_params[param_name] = new_param_values
        new_query_string = urlencode(query_params, doseq=True)
        return new_query_string

    @classmethod
    def sanitize_query_string(cls, query_string):
        query_params = parse_qs(query_string)
        blacklist = ["passwd", "token", "password", "key"]
        for param_name, param_values in query_params.items():
            new_param_values = []
            for param_value in param_values:
                if param_name in blacklist:
                    new_param_values.append("x")
                    continue
                new_param_values.append(cls.hmac(param_value))
            query_params[param_name] = new_param_values
        new_query_string = urlencode(query_params, doseq=True)
        return new_query_string

    @classmethod
    def sanitize_uri(cls, uri):
        scheme, netloc, path, query_string, fragment = urlsplit(uri)
        query_string = cls.sanitize_query_string(query_string)
        if fragment is not None and fragment != "":
            fragment = "x"
        return urlunsplit((str(scheme), str(netloc), str(path), str(query_string), str(fragment)))

    @classmethod
    def strip_uri(cls, uri):
        scheme, netloc, path, query_string, fragment = urlsplit(uri)
        query_string = cls.strip_query_string(query_string)
        if fragment is not None and fragment != "":
            fragment = cls.hmac(fragment)

        return urlunsplit((str(scheme), str(netloc), str(path), str(query_string), str(fragment)))

    @classmethod
    def sanitize_request_info(cls, request_info):
        headers = request_info.get("headers")
        if headers:
            sanitized_headers = {}
            for header_name, header_values in headers.items():
                sanitized_headers[header_name] = []
                header_name_l = header_name.lower()
                if header_name_l == "cookie":
                    for header_value in header_values:
                        base_cookie = BaseCookie(str(header_value))
                        for cookie_name, cookie_value in base_cookie.items():
                            base_cookie[cookie_name] = cls.hmac(cookie_value.coded_value)
                        sanitized_headers[header_name].append(base_cookie.output(header="", sep=';'))
                elif header_name_l == "referer":
                    for header_value in header_values:
                        sanitized_headers[header_name].append(cls.sanitize_uri(header_value))
                else:
                    sanitized_headers[header_name] = header_values
            request_info["headers"] = sanitized_headers
        uri = request_info["uri"]
        if uri:
            request_info["uri"] = cls.sanitize_uri(uri)
        post_data = request_info.get("post_data")
        if post_data:
            request_info["post_data"] = cls.sanitize_query_string(post_data)
        return request_info

    @classmethod
    def sanitize_response_info(cls, response_info):
        headers = response_info.get("headers")
        if headers:
            sanitized_headers = {}
            for header_name, header_values in headers.items():
                sanitized_headers[header_name] = []
                header_name_l = header_name.lower()
                if header_name_l == "set-cookie":
                    for header_value in header_values:
                        base_cookie = BaseCookie(str(header_value))
                        for cookie_name, cookie_value in base_cookie.items():
                            base_cookie[cookie_name] = cls.hmac(cookie_value.coded_value)
                        sanitized_headers[header_name].append(base_cookie.output(header="", sep=';').strip())
                else:
                    sanitized_headers[header_name] = header_values
            response_info["headers"] = sanitized_headers
        return response_info
